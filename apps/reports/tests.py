"""Report tests — pure aggregation helpers need Mongo; test CSV builders here."""
from django.test import TestCase
from apps.reports.export_excel import csv_response


class ExportTests(TestCase):
    def test_csv_response(self):
        resp = csv_response("t.csv", ["A", "B"], [[1, 2]])
        self.assertEqual(resp.status_code, 200)
        self.assertIn("attachment", resp["Content-Disposition"])
        self.assertIn("text/csv", resp["Content-Type"])
