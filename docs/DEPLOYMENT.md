# Deployment

> Netlify (`.netlify.app`) par host MAT karo — Netlify sirf static HTML
> host karta hai, Django + gunicorn + MongoDB nahi chala sakta.
> Is project ke liye **Render** (ya Railway/Fly/VPS) use karo.
> Root `index.html` wala localhost redirect isi galat static-hosting ki
> wajah se tha — hata diya gaya hai.

## Render (recommended)

1. MongoDB Atlas par free cluster banao, `MONGODB_URI` connection string lo.
2. Repo ko Render → New → Web Service se connect karo (`render.yaml` auto-detect hoga).
3. Render dashboard → Environment me set karo:
   - `MONGODB_URI` = Atlas string (secret, `sync: false` already yaml me hai)
   - `DJANGO_ADMIN_PATH` = obscure value, example `mgmt-x7q2/` (default `django-admin/` par mat chhodo)
   - Baki `render.yaml` se auto: `DEBUG=False`, `SECRET_KEY`, `SQLITE_PATH=/var/data/db.sqlite3`,
     `MEDIA_ROOT=/var/data/media`, 1GB disk `/var/data` par (DB + bills restart par safe).
4. Deploy ke baad Render Shell me:
   ```bash
   ADMIN_USERNAME=admin ADMIN_EMAIL=tum@mail.com ADMIN_PASSWORD='mazboot-pass' python scripts/create_admin.py
   python scripts/seed_items.py
   ```
5. Kholo: `https://tumhara-app.onrender.com/` (public), `/panel/` (admin).

Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
Start: `python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60`

## Manual VPS

1. `pip install -r requirements.txt`
2. `.env.example` → `.env`, set `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`,
   `CSRF_TRUSTED_ORIGINS=https://tumhara-domain`, `MONGODB_URI`, `MONGODB_DATABASE`.
3. `python manage.py migrate`
4. `ADMIN_USERNAME=admin ADMIN_EMAIL=a@x.com ADMIN_PASSWORD='...' python scripts/create_admin.py`
5. `python scripts/seed_items.py`
6. `python manage.py collectstatic`
7. `gunicorn config.wsgi:application --bind 0.0.0.0:8000`
8. nginx se `/static/` + `/media/` serve karo, HTTPS lagao.

## Postgres (optional, bada setup)

- `DATABASE_URL=postgres://...` set karte hi SQLite ki jagah Postgres use hoga
  (`dj-database-url` + `psycopg` already `requirements.txt` me hai).
- Bina `DATABASE_URL` ke `SQLITE_PATH` (disk) use hota hai.

## Production storage

Bade scale par S3: `apps/uploads/storage.py` ke same 3 functions
(`save_bill_file` / `delete_bill_file` / `bill_url`) ko boto3 se implement
karo — templates already `bill_url` filter use karte hain, kuch tootega nahi.
