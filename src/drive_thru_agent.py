"""DriveThruAgent - Orchestrator for McDonald's drive-thru ordering.

This module provides the DriveThruAgent class that brings together all components
to create a complete drive-thru order taking agent. It defines the agent's persona,
registers tools, and coordinates the conversation flow.

Key Principles:
- Orchestration: Wires components together, doesn't implement logic
- Owns State: Owns OrderStateManager instance (composition)
- Receives Dependencies: Gets MenuProvider, DriveThruLLM via DI
- Defines Persona: Sets instructions and conversation style
"""

from livekit.agents import Agent
from loguru import logger

from drive_thru_llm import DriveThruLLM
from menu_provider import MenuProvider
from order_state_manager import OrderStateManager
from tools.order_tools import create_order_tools


class DriveThruAgent(Agent):
    """McDonald's drive-thru order taking agent.

    Orchestrates:
    - OrderStateManager (owns instance per session)
    - Tools (created with dependencies)
    - DriveThruLLM (wrapped LLM with context injection)
    - Instructions/persona

    This agent extends LiveKit's Agent class and provides all necessary
    components for a complete drive-thru ordering experience.
    """

    def __init__(
        self,
        session_id: str,
        llm: DriveThruLLM,
        menu_provider: MenuProvider,
        output_dir: str = "orders",
    ) -> None:
        """Initialize drive-thru agent.

        Args:
            session_id: Unique session ID
            llm: DriveThruLLM (wrapped LLM)
            menu_provider: MenuProvider for menu access
            output_dir: Directory for order files
        """
        # Store dependencies first
        self._llm = llm
        self._menu_provider = menu_provider
        self._session_id = session_id

        # Create OrderStateManager for this session (agent owns it)
        self._order_state = OrderStateManager(
            session_id=session_id, output_dir=output_dir
        )

        # Create tools with dependencies injected BEFORE calling super().__init__()
        self._tools = create_order_tools(
            order_state=self._order_state, menu_provider=self._menu_provider
        )

        # Log tool creation for diagnostics
        logger.info(f"Created {len(self._tools)} tools for drive-thru agent")
        logger.debug(f"Tool types: {[type(t).__name__ for t in self._tools]}")

        # Initialize Agent with instructions, tools, AND LLM
        logger.debug(f"Initializing Agent with LLM type: {type(llm).__name__}")
        logger.debug(f"Number of tools being passed: {len(self._tools)}")

        super().__init__(
            instructions=self._get_instructions(), tools=self._tools, llm=llm
        )

        logger.info(f"DriveThruAgent initialized successfully for session {session_id}")

    def _get_instructions(self) -> str:
        """Get agent instructions/persona.

        Returns:
            Complete agent instructions including persona, responsibilities,
            and guidelines.
        """
        return """You are a friendly and efficient McDonald's drive-thru order taker.

Your responsibilities:
1. Greet customers warmly when they arrive
2. Listen carefully to their order and add items one at a time
3. When the customer is done ordering, use complete_order function
4. Read back the complete order summary
5. Thank the customer

CRITICAL TOOL USAGE RULES:
- ALWAYS call add_item_to_order with item_name, modifiers, and quantity together
- If customer says item with modifiers ("Big Mac with extra cheese"), extract them and call the tool immediately
- If customer says just the item name ("Big Mac"), you MAY ask about modifiers first OR just add it with empty modifiers
- Once you've added an item (tool returns success), just acknowledge it - do NOT call the tool again
- When customer says "No thanks" or "Nothing else" after an item is added, that means they're declining to add more items - do NOT call any tool
- When customer says "That's all" or "I'm done", call complete_order

CRITICAL: When customer declines modifiers ("No thanks", "No", "That's it"):
- You MUST still call add_item_to_order with the item name they mentioned earlier
- Use modifiers=[] (empty list) when they don't want modifications
- Example:
  - User: "I want a Big Mac"
  - You: "Would you like any modifications?"
  - User: "No thanks"
  - You call: add_item_to_order(item_name="Big Mac", modifiers=[], quantity=1)
  - NEVER call: add_item_to_order() without item_name - this will fail!

Examples of CORRECT behavior:

Example 1 - Customer mentions modifiers upfront:
- User: "I want a Big Mac with extra cheese"
- You call: add_item_to_order(item_name="Big Mac", modifiers=["Extra Cheese"], quantity=1)
- Tool returns: "Added one Big Mac with Extra Cheese to your order."
- You say: "Got it! Anything else?"
- User: "No thanks"
- You say: "Alright! Would you like to complete your order?"
- (Do NOT call any tool when they say "No thanks" to "Anything else?")

Example 2 - Ask about modifiers first:
- User: "Can I get a Big Mac?"
- You: "Sure! Would you like any modifications to that Big Mac?"
- User: "No thanks"
- You call: add_item_to_order(item_name="Big Mac", modifiers=[], quantity=1)
- Tool returns: "Added one Big Mac to your order."
- You say: "Got it! Anything else?"

Example 3 - Multiple items:
- User: "I'll take a Big Mac and large fries"
- You call: add_item_to_order(item_name="Big Mac", modifiers=[], quantity=1)
- Tool returns: "Added one Big Mac to your order."
- You call: add_item_to_order(item_name="Large French Fries", modifiers=[], quantity=1)
- Tool returns: "Added one Large French Fries to your order."
- You say: "Got a Big Mac and large fries. Anything else?"

Guidelines:
- Be concise and natural - avoid overly formal language
- NEVER call add_item_to_order without item_name - it's a required parameter
- When customer says "No" or "No thanks" to "Anything else?", they're declining more items - do NOT call a tool
- Use exact menu item names when confirming
- If customer mentions an item not on the menu, politely inform them

Remember: You have access to the complete menu through context injection.
"""

    @property
    def agent(self) -> Agent:
        """Get the LiveKit Agent instance.

        Returns:
            The Agent instance (self, since this class extends Agent)
        """
        return self

    @property
    def order_state(self) -> OrderStateManager:
        """Get the order state manager.

        Returns:
            The OrderStateManager instance for this session
        """
        return self._order_state

    @property
    def llm(self) -> DriveThruLLM:
        """Get the DriveThruLLM instance.

        Returns:
            The wrapped LLM with menu context injection
        """
        return self._llm

    @property
    def tools(self) -> list:
        """Get the order management tools.

        Returns:
            List of LiveKit FunctionTool instances
        """
        return self._tools

    async def close(self) -> None:
        """Clean up resources.

        This method can be extended to add cleanup logic if needed in the future.
        """
        pass
