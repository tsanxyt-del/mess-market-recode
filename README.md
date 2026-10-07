# Mess Market Management System

Advanced Hostel Mess Market Management — **Django + MongoDB (PyMongo) + Vanilla JS**.
No React/Vue/Angular. All totals aggregated server-side from actual records.

## Quick start

```bash
pip install -r requirements.txt
python manage.py migrate
python scripts/create_admin.py        # or set ADMIN_USERNAME/ADMIN_EMAIL/ADMIN_PASSWORD env
python scripts/seed_items.py          # default item master (needs MongoDB running)
python manage.py runserver
```

- Public: http://127.0.0.1:8000/ (MESS MARKET RECORD, no login)
- Admin: http://127.0.0.1:8000/panel/ → login at `/accounts/login/`
- Requires MongoDB at `MONGODB_URI` (default `mongodb://localhost:27017`).
  Pages degrade gracefully if Mongo is down, but records need it.

## Structure

- `config/` — settings, urls, Mongo singleton (`mongo.py`)
- `apps/accounts/` — login/logout/profile/password (Django auth, hashed)
- `apps/market/` — records CRUD, selectors (aggregation), validators, JSON APIs
- `apps/items/` — item master (add/edit/disable/search)
- `apps/reports/` — monthly/daily/item-wise + CSV/Excel/PDF export
- `apps/uploads/` — bill upload (type+size validated, MEDIA storage, S3-ready abstraction)
- `apps/dashboard/` — public pages + admin dashboard
- `apps/notifications/` — audit log in Mongo
- `templates/`, `static/` (vanilla CSS/JS), `scripts/`, `tests/`, `docs/`, `database/`

## Key rules enforced

- `total = quantity × rate` computed in **backend** (`validators.py`); JS live-total is UX only.
- `year`/`month` auto-derived from `purchase_date` — no cross-month mixing.
- Soft delete (`deleted_at`); public totals exclude deleted.
- Monthly/daily/item totals via MongoDB aggregation — never hard-coded, never in JS.
- Pagination + server-side filtering for thousands of records.

## Tests

```bash
python manage.py test
```

## Docs

`docs/API.md`, `docs/DATABASE.md`, `docs/DEPLOYMENT.md`, `docs/BACKUP.md`, `docs/SECURITY.md`.
