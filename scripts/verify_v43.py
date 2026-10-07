import os, sys, logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
logging.disable(logging.CRITICAL)
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()
from django.test import Client
from django.test.utils import override_settings

s = override_settings(ALLOWED_HOSTS=['testserver', 'localhost'], DEBUG=True)
s.enable()
c = Client()
checks = [
    ('/', ['app-tabbar', 'offlineBar', 'monthForm']),
    ('/months/', ['year-head', 'app-tabbar']),
    ('/month/2026/10/', ['data-share', 'share.js']),
    ('/day/2026-10-01/', ['day-pager', 'data-share', 'share.js']),
    ('/search/', ['chip-row', 'share.js']),
    ('/reports/', ['spendChart', 'data-share']),
]
for u, keys in checks:
    r = c.get(u)
    h = r.content.decode()
    missing = [k for k in keys if k not in h]
    print(r.status_code, u, 'MISSING:' + ','.join(missing) if missing else 'OK')
