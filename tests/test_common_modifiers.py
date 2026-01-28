"""Tests for common_modifiers module."""

import pytest

from common_modifiers import (
    COMMON_MODIFIERS,
    get_common_modifiers_for_category,
    is_common_modifier_for_category,
)


class TestIsCommonModifierForCategory:
    """Tests for is_common_modifier_for_category function."""

    def test_exact_match_case_insensitive(self):
        """Test exact match works with different cases."""
        is_valid, matched = is_common_modifier_for_category(
            "extra cheese", "Beef & Pork"
        )
        assert is_valid is True
        assert matched == "Extra Cheese"

        is_valid, matched = is_common_modifier_for_category(
            "EXTRA CHEESE", "Beef & Pork"
        )
        assert is_valid is True
        assert matched == "Extra Cheese"

    def test_fuzzy_match_typo(self):
        """Test fuzzy matching handles typos."""
        # Use lower threshold for typos (score is ~70 for "pickels" vs "pickles")
        is_valid, matched = is_common_modifier_for_category(
            "no pickels", "Beef & Pork", threshold=70
        )
        assert is_valid is True
        assert matched == "No Pickles"

    def test_invalid_modifier(self):
        """Test invalid modifier returns False."""
        is_valid, matched = is_common_modifier_for_category(
            "anchovies", "Beef & Pork"
        )
        assert is_valid is False
        assert matched is None

    def test_invalid_category(self):
        """Test invalid category returns False."""
        is_valid, matched = is_common_modifier_for_category(
            "Extra Cheese", "Unknown Category"
        )
        assert is_valid is False
        assert matched is None

    def test_category_specific_modifiers(self):
        """Test that modifiers are category-specific."""
        # Egg Whites is valid for Breakfast but not Beef & Pork
        is_valid, _ = is_common_modifier_for_category("Egg Whites", "Breakfast")
        assert is_valid is True

        is_valid, _ = is_common_modifier_for_category("Egg Whites", "Beef & Pork")
        assert is_valid is False

    def test_all_categories_have_modifiers(self):
        """Test that all categories in COMMON_MODIFIERS have at least some modifiers."""
        for category, modifiers in COMMON_MODIFIERS.items():
            assert len(modifiers) > 0, f"Category '{category}' has no modifiers"

    @pytest.mark.parametrize(
        "modifier,category,expected",
        [
            ("Extra Cheese", "Beef & Pork", True),
            ("No Pickles", "Beef & Pork", True),
            ("Extra Mayo", "Chicken & Fish", True),
            ("Egg Whites", "Breakfast", True),
            ("No Ice", "Beverages", True),
            ("Decaf", "Coffee & Tea", True),
            ("Extra Caramel", "Desserts", True),
            ("No Whipped Cream", "Smoothies & Shakes", True),
            ("Extra Salt", "Snacks & Sides", True),
        ],
    )
    def test_common_modifiers_by_category(self, modifier, category, expected):
        """Test common modifiers across different categories."""
        is_valid, matched = is_common_modifier_for_category(modifier, category)
        assert is_valid == expected


class TestGetCommonModifiersForCategory:
    """Tests for get_common_modifiers_for_category function."""

    def test_valid_category(self):
        """Test getting modifiers for valid category."""
        modifiers = get_common_modifiers_for_category("Beef & Pork")
        assert len(modifiers) > 0
        assert "Extra Cheese" in modifiers
        assert "No Pickles" in modifiers

    def test_invalid_category(self):
        """Test getting modifiers for invalid category returns empty list."""
        modifiers = get_common_modifiers_for_category("Unknown Category")
        assert modifiers == []

    def test_all_categories_accessible(self):
        """Test that all categories can be accessed."""
        for category in COMMON_MODIFIERS.keys():
            modifiers = get_common_modifiers_for_category(category)
            assert len(modifiers) > 0
