"""Market unit tests — pure logic (no Mongo needed) + validation."""
from django.test import TestCase
from apps.market.validators import (validate_record_payload, compute_total, MarketValidationError)
from apps.market.calculations import calc_total, summarize


class CalculationTests(TestCase):
    def test_total(self):
        self.assertEqual(compute_total(50, 45), 2250)
        self.assertEqual(calc_total(20, 100), 2000)

    def test_backend_recomputes_total(self):
        clean = validate_record_payload("x", "Rice", 50, "KG", 45, "2026-10-01")
        self.assertEqual(clean["total"], 2250)
        self.assertEqual(clean["year"], 2026)
        self.assertEqual(clean["month"], 10)

    def test_month_derived_from_date(self):
        for ds, m in [("2026-10-01", 10), ("2026-11-01", 11)]:
            clean = validate_record_payload("x", "Rice", 1, "KG", 10, ds)
            self.assertEqual(clean["month"], m)

    def test_invalid_quantity(self):
        with self.assertRaises(MarketValidationError):
            validate_record_payload("x", "Rice", 0, "KG", 10, "2026-10-01")
        with self.assertRaises(MarketValidationError):
            validate_record_payload("x", "Rice", -5, "KG", 10, "2026-10-01")

    def test_invalid_unit(self):
        with self.assertRaises(MarketValidationError):
            validate_record_payload("x", "Rice", 5, "LIGHTYEAR", 10, "2026-10-01")

    def test_summarize(self):
        s = summarize([{"total": 100, "quantity": 5}, {"total": 200, "quantity": 10}])
        self.assertEqual(s["total_amount"], 300)
        self.assertEqual(s["count"], 2)
