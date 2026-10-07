"""Items tests (validators only — no DB needed)."""
from django.test import TestCase
from apps.items.validators import validate_item_name, validate_default_unit, ItemValidationError


class ItemValidatorTests(TestCase):
    def test_valid(self):
        self.assertEqual(validate_item_name("  Rice "), "Rice")
        self.assertEqual(validate_default_unit("kg"), "KG")

    def test_invalid(self):
        with self.assertRaises(ItemValidationError):
            validate_item_name("  ")
        with self.assertRaises(ItemValidationError):
            validate_default_unit("LIGHTYEAR")
