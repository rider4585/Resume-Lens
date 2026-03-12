# Database migrations (Alembic)

Resume Lens uses [Alembic](https://alembic.sqlalchemy.org/) for DB schema changes so the database is easy to maintain and scale.

## First-time setup

1. Set `DATABASE_URL` in `.env` (e.g. SQLite or MySQL).
2. From the **project root** run:

   ```bash
   alembic upgrade head
   ```

   This creates the tables (`saved_jds`, `resumes`, `matches`) if they don’t exist.

## Common commands

| Command | Description |
|--------|-------------|
| `alembic upgrade head` | Apply all pending migrations (bring DB to latest). |
| `alembic downgrade -1` | Undo the last migration. |
| `alembic current` | Show current revision. |
| `alembic history` | List revisions. |
| `alembic revision -m "add xyz"` | Create a new empty revision to edit. |
| `alembic revision --autogenerate -m "add xyz"` | Generate a revision from model changes (review before applying). |

## Adding a new migration

1. Change the SQLAlchemy models in `app/models/match.py` (or add new models).
2. From project root:

   ```bash
   alembic revision --autogenerate -m "describe your change"
   ```

3. Open the new file under `alembic/versions/`, fix any missing or wrong steps (especially with renames or data changes).
4. Apply it:

   ```bash
   alembic upgrade head
   ```

## Project layout

- `alembic.ini` – Alembic config (script location, logging). The DB URL is set from `.env` in `alembic/env.py`.
- `alembic/env.py` – Uses `app.config.get_settings().database_url` and `app.models.db.Base.metadata`.
- `alembic/versions/` – One file per migration; apply in order with `alembic upgrade head`.
