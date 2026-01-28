"""LiveKit Tools for order management in the drive-thru agent.

This module provides the coordination layer between the LLM and the order management
system. Tools validate inputs using menu_validation, then delegate to OrderStateManager
for state mutations.

Key Principles:
- Thin coordination layer: orchestrate, don't implement logic
- Validate before mutate: always validate using menu_validation
- Return helpful string responses for the LLM to relay to users
"""

from livekit.agents import llm
from livekit.agents.llm import function_tool
from loguru import logger
from rapidfuzz import fuzz, process

from menu_provider import MenuProvider
from menu_validation import validate_order_item
from order_state_manager import OrderStateManager


def create_order_tools(
    order_state: OrderStateManager,
    menu_provider: MenuProvider,
) -> list[llm.Tool]:
    """
    Create LiveKit Tool instances with dependencies injected.

    This factory function uses closures to inject the OrderStateManager and
    MenuProvider dependencies into the tool functions. This allows each session
    to have its own OrderStateManager while sharing a single MenuProvider.

    Args:
        order_state: OrderStateManager instance for this session
        menu_provider: MenuProvider instance (shared singleton)

    Returns:
        List of FunctionTool objects that can be registered with an Agent

    Example:
        >>> menu_provider = MenuProvider("menu.json")
        >>> order_state = OrderStateManager(session_id="abc-123")
        >>> tools = create_order_tools(order_state, menu_provider)
        >>> agent = Agent(tools=tools, ...)
    """

    @function_tool(
        name="add_item_to_order",
        description=(
            "Add a menu item to the customer's order. Always validate the item "
            "exists on the menu before adding. Use this when the customer requests "
            "a menu item. You don't need to specify the category - it will be "
            "automatically determined from the item name."
        ),
        raw_schema={
            "name": "add_item_to_order",
            "description": (
                "Add a menu item to the customer's order. Always validate the item "
                "exists on the menu before adding. Use this when the customer requests "
                "a menu item. You don't need to specify the category - it will be "
                "automatically determined from the item name."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "item_name": {
                        "type": "string",
                        "description": "The exact name of the menu item (e.g., 'Big Mac', 'Egg McMuffin')",
                    },
                    "modifiers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of modifiers or customizations (e.g., ['No Pickles', 'Extra Sauce'])",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of this item to add",
                        "default": 1,
                        "minimum": 1,
                    },
                },
                "required": ["item_name"],
            },
        },
    )
    async def add_item_to_order(
        item_name: str,
        modifiers: list[str] | None = None,
        quantity: int = 1,
    ) -> str:
        logger.debug(f"add_item_to_order called: item_name={item_name}, modifiers={modifiers}, quantity={quantity}")
        """
        Add a menu item to the customer's order.

        This tool validates the item against the menu before adding it to the order.
        If validation fails, it returns an error message without mutating state.
        The category is automatically determined by searching the menu.

        Args:
            item_name: Name of the menu item (e.g., 'Big Mac')
            modifiers: Optional list of modifiers (e.g., ['No Pickles', 'Extra Sauce'])
            quantity: Number of items to add (default: 1)

        Returns:
            Confirmation message if successful, error message if validation fails
        """
        # Normalize inputs
        modifiers = modifiers or []
        logger.debug(f"Looking up item: {item_name}")

        # Get all items from the menu
        all_items = []
        for category_name in menu_provider.get_all_categories():
            all_items.extend(menu_provider.get_category(category_name))

        # Try exact match first (case-insensitive)
        exact_match = None
        for item in all_items:
            if item.item_name.lower() == item_name.lower():
                exact_match = item
                break

        if exact_match:
            matched_item = exact_match
            category = matched_item.category_name
            logger.debug(f"Found exact match: {matched_item.item_name} in category {category}")
        else:
            # Use fuzzy matching with rapidfuzz (case-insensitive)
            item_names = [item.item_name for item in all_items]
            # Create lowercase mapping for case-insensitive search
            lowercase_mapping = {name.lower(): name for name in item_names}
            lowercase_names = list(lowercase_mapping.keys())

            fuzzy_result = process.extractOne(
                item_name.lower(),  # Convert query to lowercase
                lowercase_names,
                scorer=fuzz.ratio,
                score_cutoff=80  # Slightly lower threshold for better matches (was 85)
            )

            if fuzzy_result:
                matched_lowercase, score, _ = fuzzy_result
                # Map back to original case
                original_name = lowercase_mapping[matched_lowercase]
                # Find the item with this name
                matched_item = next(item for item in all_items if item.item_name == original_name)
                category = matched_item.category_name
                logger.debug(f"Found fuzzy match: {matched_item.item_name} (score: {score}) in category {category}")
            else:
                # No match found
                logger.warning(f"Item '{item_name}' not found in menu")
                return f"Sorry, I couldn't find '{item_name}' on our menu. Could you try a different item?"

        # Now validate with the found category
        validation_result = validate_order_item(
            item_name=matched_item.item_name,
            category=category,
            modifiers=modifiers,
            menu=menu_provider.get_menu(),
            fuzzy_threshold=85,
        )

        # If invalid, return error message without mutating state
        if not validation_result.is_valid:
            logger.warning(f"Validation failed: {validation_result.error_message}")
            return f"Sorry, I couldn't add that item: {validation_result.error_message}"

        # Use matched item from validation (might be fuzzy matched to correct spelling)
        validated_item = validation_result.matched_item
        logger.debug(f"Validation successful, matched item: {validated_item.item_name}")

        order_state.add_item(
            item_name=validated_item.item_name,  # Use exact match from menu
            category=category,
            modifiers=modifiers,
            quantity=quantity,
        )

        # Build confirmation message
        modifier_text = ""
        if modifiers:
            modifier_text = f" with {', '.join(modifiers)}"

        if quantity > 1:
            response = f"Added {quantity} {validated_item.item_name}{modifier_text} to your order."
        else:
            response = f"Added one {validated_item.item_name}{modifier_text} to your order."

        logger.info(f"Successfully added item: {response}")
        return response

    @function_tool(
        name="complete_order",
        description=(
            "Complete the order and generate the final order summary. "
            "Call this when the customer says they're done ordering."
        ),
        raw_schema={
            "name": "complete_order",
            "description": (
                "Complete the order and generate the final order summary. "
                "Call this when the customer says they're done ordering."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    )
    async def complete_order() -> str:
        logger.debug("complete_order called")
        """
        Complete the order and generate the final order summary.

        This tool should be called when the customer indicates they're done ordering.
        It finalizes the order and writes the final JSON file.

        Returns:
            Order summary if successful, prompt to add items if order is empty
        """
        # Check if order is empty
        if order_state.is_empty():
            logger.debug("Order is empty, cannot complete")
            return "Your order is empty. Would you like to add something?"

        # Complete order (writes final JSON)
        final_order = order_state.complete_order()

        # Build summary
        summary = final_order["order_summary"]
        total_items = final_order["total_items"]

        response = f"Order complete! You ordered: {summary}. Total items: {total_items}. Thank you!"
        logger.info(f"Order completed: {response}")
        return response

    @function_tool(
        name="remove_item_from_order",
        description=(
            "Remove an item from the order. Useful when customer wants to "
            "cancel an item. If multiple items with the same name exist, "
            "removes the most recently added one."
        ),
        raw_schema={
            "name": "remove_item_from_order",
            "description": (
                "Remove an item from the order. Useful when customer wants to "
                "cancel an item. If multiple items with the same name exist, "
                "removes the most recently added one."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "item_name": {
                        "type": "string",
                        "description": "Name of the item to remove (e.g., 'Big Mac')",
                    },
                },
                "required": ["item_name"],
            },
        },
    )
    async def remove_item_from_order(item_name: str) -> str:
        logger.debug(f"remove_item_from_order called: item_name={item_name}")
        """
        Remove an item from the order.

        Useful when a customer wants to cancel or remove an item. If multiple items
        with the same name exist, this removes the most recently added one.

        Args:
            item_name: Name of the item to remove (e.g., 'Big Mac')

        Returns:
            Confirmation message if successful, error message if item not found
        """
        # Find item by name (use latest item with that name)
        items = order_state.get_items()
        item_to_remove = None

        # Search from end (most recent items first)
        for item in reversed(items):
            if item.item_name.lower() == item_name.lower():
                item_to_remove = item
                break

        if item_to_remove is None:
            logger.debug(f"Item '{item_name}' not found in order")
            return f"I don't see '{item_name}' in your order."

        # Remove item
        success = order_state.remove_item(item_to_remove.item_id)

        if success:
            logger.info(f"Removed {item_name} from order")
            return f"Removed {item_name} from your order."
        else:
            logger.warning(f"Failed to remove {item_name}")
            return f"Couldn't remove {item_name}. Please try again."

    # Return decorated functions (they are now FunctionTool instances)
    tools = [add_item_to_order, complete_order, remove_item_from_order]
    logger.debug(f"Created {len(tools)} order tools")
    return tools
