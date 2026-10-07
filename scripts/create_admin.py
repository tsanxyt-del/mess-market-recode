"""Create a Django admin/superuser non-interactively (for first setup)."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django  # noqa: E402
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

User = get_user_model()
username = os.getenv("ADMIN_USERNAME", "admin")
email = os.getenv("ADMIN_EMAIL", "admin@example.com")
password = os.getenv("ADMIN_PASSWORD", "Admin@123")

if User.objects.filter(username=username).exists():
    print(f"User '{username}' already exists.")
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created.")
