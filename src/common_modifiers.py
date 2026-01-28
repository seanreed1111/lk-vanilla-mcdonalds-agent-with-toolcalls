"""Common modifiers available for menu items without predefined modifiers.

This module defines standard modifiers that are commonly available across
McDonald's menu categories. These are used as a fallback when an item
doesn't have predefined modifiers in the menu data.
"""

from rapidfuzz import fuzz, process

# Common modifiers by category
COMMON_MODIFIERS = {
    "Beef & Pork": [
        "Extra Cheese",
        "No Cheese",
        "Extra Pickles",
        "No Pickles",
        "Extra Onions",
        "No Onions",
        "Extra Ketchup",
        "No Ketchup",
        "Extra Mustard",
        "No Mustard",
        "Extra Lettuce",
        "No Lettuce",
        "Extra Tomato",
        "No Tomato",
        "Extra Mac Sauce",
        "No Mac Sauce",
        "Add Bacon",
        "No Bacon",
    ],
    "Chicken & Fish": [
        "Extra Cheese",
        "No Cheese",
        "Extra Lettuce",
        "No Lettuce",
        "Extra Mayo",
        "No Mayo",
        "Extra Pickles",
        "No Pickles",
        "Spicy",
        "No Sauce",
        "Extra Sauce",
        "Add Bacon",
        "No Bacon",
    ],
    "Breakfast": [
        "Egg Whites",
        "No Egg",
        "Extra Egg",
        "Add Bacon",
        "No Bacon",
        "Add Sausage",
        "No Sausage",
        "Extra Cheese",
        "No Cheese",
        "No Butter",
        "Extra Hash Brown",
    ],
    "Snacks & Sides": [
        "Extra Salt",
        "No Salt",
        "Extra Sauce",
        "No Sauce",
        "Ketchup",
        "Ranch",
        "BBQ Sauce",
        "Sweet & Sour Sauce",
        "Honey Mustard",
    ],
    "Beverages": [
        "No Ice",
        "Light Ice",
        "Extra Ice",
        "No Sugar",
        "Extra Sugar",
        "No Cream",
        "Extra Cream",
    ],
    "Coffee & Tea": [
        "No Sugar",
        "Extra Sugar",
        "No Cream",
        "Extra Cream",
        "Skim Milk",
        "Whole Milk",
        "Almond Milk",
        "Decaf",
    ],
    "Desserts": [
        "Extra Caramel",
        "Extra Chocolate",
        "Extra Whipped Cream",
        "No Whipped Cream",
        "Extra Sprinkles",
    ],
    "Smoothies & Shakes": [
        "No Whipped Cream",
        "Extra Whipped Cream",
        "No Cherry",
        "Extra Syrup",
        "Light Syrup",
    ],
}


def is_common_modifier_for_category(
    modifier: str, category: str, threshold: int = 85
) -> tuple[bool, str | None]:
    """Check if a modifier is a common modifier for the given category.

    Uses fuzzy matching to handle variations in spelling and case.

    Args:
        modifier: The modifier to check (e.g., "extra cheese", "Extra Cheese")
        category: The menu category (e.g., "Beef & Pork")
        threshold: Minimum fuzzy match score (0-100) to accept

    Returns:
        Tuple of (is_valid, matched_modifier_name)
        - is_valid: True if modifier is common for this category
        - matched_modifier_name: The canonical name of the matched modifier, or None

    Examples:
        >>> is_common_modifier_for_category("extra cheese", "Beef & Pork")
        (True, "Extra Cheese")
        >>> is_common_modifier_for_category("anchovies", "Beef & Pork")
        (False, None)
        >>> is_common_modifier_for_category("no pickels", "Beef & Pork", threshold=85)
        (True, "No Pickles")  # Fuzzy match handles typo
    """
    if category not in COMMON_MODIFIERS:
        return (False, None)

    common_modifiers = COMMON_MODIFIERS[category]

    # Try exact match first (case-insensitive)
    for common_mod in common_modifiers:
        if common_mod.lower() == modifier.lower():
            return (True, common_mod)

    # Fall back to fuzzy matching
    result = process.extractOne(
        modifier, common_modifiers, scorer=fuzz.ratio, score_cutoff=threshold
    )

    if result is None:
        return (False, None)

    matched_modifier, score, _ = result
    return (True, matched_modifier)


def get_common_modifiers_for_category(category: str) -> list[str]:
    """Get all common modifiers for a given category.

    Args:
        category: The menu category (e.g., "Beef & Pork")

    Returns:
        List of common modifier names for the category, or empty list if
        category not found

    Examples:
        >>> get_common_modifiers_for_category("Beef & Pork")
        ["Extra Cheese", "No Cheese", "Extra Pickles", ...]
        >>> get_common_modifiers_for_category("Unknown Category")
        []
    """
    return COMMON_MODIFIERS.get(category, [])
