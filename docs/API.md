# JSON APIs

Public (no login):

- `GET /panel/market/api/records/?year=2026&month=10&page=1` — paginated records
- `GET /panel/market/api/months/` — available months + years
- `GET /panel/market/api/month/<year>/<month>/` — monthly summary (days, totals, avg, high/low)
- `GET /panel/market/api/day/<YYYY-MM-DD>/` — day detail
- `GET /panel/market/api/search/?q=rice` — search
- `GET /panel/items/api/list/?q=` — item dropdown
- `GET /panel/reports/api/data/?kind=monthly|daily|item`

Admin (session auth, CSRF):

- `POST /panel/market/api/create/` `{purchase_date,item_id,item_name,quantity,unit,rate,remark}`
- `POST /panel/market/api/<id>/update/` — same fields (partial OK)
- `POST /panel/market/api/<id>/delete/` — soft delete
- `GET /panel/api/stats/` — dashboard stats

All totals are computed server-side (`quantity × rate`); any `total`
sent by the browser is ignored.
