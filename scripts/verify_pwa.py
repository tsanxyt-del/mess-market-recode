import os, sys, django, logging, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
logging.disable(logging.CRITICAL)
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()
from django.test import Client
from django.test.utils import override_settings

s = override_settings(ALLOWED_HOSTS=['testserver', 'localhost'], DEBUG=True)
s.enable()
c = Client()
r = c.get('/manifest.json')
print(r.status_code, r['Content-Type'])
m = json.loads(b''.join(r.streaming_content))
print('manifest:', m['name'], '| icons:', len(m['icons']), '| display:', m['display'])
r = c.get('/sw.js')
print(r.status_code, r['Content-Type'], 'len', sum(len(x) for x in r.streaming_content))
r = c.get('/')
h = r.content.decode()
print(r.status_code, 'manifest-link:', 'manifest' in h,
      '| install-btn:', 'data-install-app' in h,
      '| tabbar:', 'app-tabbar' in h)
