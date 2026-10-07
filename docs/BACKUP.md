# Backup & Restore

Run `python scripts/backup_database.py`:

- MongoDB: `mongodump --uri=$MONGODB_URI --db=$MONGODB_DATABASE`
- Media: zips `media/` separately.

Restore:

- `mongorestore --uri=$MONGODB_URI --db=$MONGODB_DATABASE backups/<ts>/mongo/<db>/`
- Unzip `media.zip` back to `media/`.

Schedule the script via cron/Task Scheduler daily.
