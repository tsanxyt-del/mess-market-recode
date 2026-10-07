"""Upload validation tests (no DB needed)."""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.uploads.validators import validate_bill_file, UploadValidationError


class UploadValidationTests(TestCase):
    def test_valid_jpg(self):
        f = SimpleUploadedFile("bill.jpg", b"x" * 100, content_type="image/jpeg")
        self.assertEqual(validate_bill_file(f), "jpg")

    def test_invalid_type(self):
        f = SimpleUploadedFile("bill.exe", b"x" * 100, content_type="application/octet-stream")
        with self.assertRaises(UploadValidationError):
            validate_bill_file(f)

    def test_too_large(self):
        from django.conf import settings
        f = SimpleUploadedFile("bill.jpg", b"x" * (settings.MAX_UPLOAD_SIZE + 1), content_type="image/jpeg")
        with self.assertRaises(UploadValidationError):
            validate_bill_file(f)
