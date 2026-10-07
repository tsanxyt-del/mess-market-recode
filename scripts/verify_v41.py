import os, sys, logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
logging.disable(logging.CRITICAL)
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()
from django.test import Client
from django.test.utils import override_settings
from django.contrib.auth import get_user_model

s = override_settings(ALLOWED_HOSTS=['testserver', 'localhost'], DEBUG=True)
s.enable()
c = Client()
for u in ['/', '/months/', '/accounts/login/']:
    r = c.get(u)
    h = r.content.decode()
    print(r.status_code, u, '| icon-toggle:', 'icon-btn' in h)
u = get_user_model().objects.get(username='admin')
c.force_login(u)
for x in ['/panel/', '/panel/market/', '/panel/activity/']:
    r = c.get(x)
    h = r.content.decode()
    print(r.status_code, x, '| bill-col:', 'Bill' in h if 'market' in x else '-')
