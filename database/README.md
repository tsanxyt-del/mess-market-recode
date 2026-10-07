# Database

Auth/sessions use SQLite via Django ORM (`db.sqlite3`).
All business data uses **MongoDB** via PyMongo (`config/mongo.py`).

Collections:

- `market_records` — purchase_date, year, month (auto-derived), item_id,
  item_name, quantity, unit, rate, total (backend-computed), bill_file,
  remark, created_at, updated_at, deleted_at (soft delete)
- `items` — name, name_lower (unique), default_unit, is_active
- `notifications` — audit log of admin events

Indexes (`database/indexes.py`, auto-created on boot):

- market_records: purchase_date, (year, month), item_id, created_at, item_name
- items: name_lower (unique)

Totals are NEVER stored per-month — always aggregated from records.
