# Database (MongoDB)

See `database/README.md` for collections + indexes.

Connection: `MONGODB_URI` / `MONGODB_DATABASE` in `.env`, singleton in
`config/mongo.py`. Django auth stays on SQLite — only business data is in Mongo.
