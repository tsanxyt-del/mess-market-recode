# Security

- Django session auth; passwords hashed (PBKDF2). No plain-text storage.
- All admin HTML views use `login_required`; admin JSON uses session check (401).
- CSRF enforced on all POST forms + AJAX (`csrf.js` sends `X-CSRFToken`).
- Server-side validation for quantity/rate/unit/date; totals recomputed in backend.
- File uploads: extension allowlist (jpg/jpeg/png/webp/pdf) + size cap
  (`MAX_UPLOAD_SIZE`) + content-type check. Files stored on disk, only the
  path is kept in MongoDB.
- `.env` holds `SECRET_KEY`, `MONGODB_URI` — never rendered to templates/JS.
- Generic 404/500 pages leak no internals. Public API is read-only.
- For production: `DEBUG=False`, HTTPS, `SECURE_*` flags (already wired),
  rotate `SECRET_KEY`, restrict MongoDB network access.
