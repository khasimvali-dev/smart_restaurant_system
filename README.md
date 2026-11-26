# Smart Restaurant Billing & Analytics System

A local-only (no cloud) restaurant/cafe/hotel billing and analytics system,
built with Flask, SQLAlchemy, MySQL (with a zero-config SQLite fallback for
first run), Pandas, and Plotly.

See `docs/ROADMAP.md` for an honest breakdown of what's built vs. what's
scoped as future work.

---

## 1. Quick Start (fastest path - SQLite, no MySQL needed)

```bash
cd smart_restaurant_system
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env              # defaults to USE_SQLITE_FALLBACK=true

export FLASK_APP=run.py           # Windows (PowerShell): $env:FLASK_APP="run.py"
flask seed-db                     # creates tables + demo data (30 days of sample bills)

python run.py                     # -> http://127.0.0.1:5000
```

Log in with the demo accounts the seed script creates:

| Username | Password | Role |
|---|---|---|
| `admin` | `Admin@123` | Admin |
| `cashier` | `Cashier@123` | Cashier |

**Change these passwords before using this for anything real.**

---

## 2. Running against real local MySQL

1. Install MySQL Server locally and make sure it's running on `127.0.0.1:3306`.
2. Create the database and a user:
   ```sql
   CREATE DATABASE smart_restaurant_db CHARACTER SET utf8mb4;
   CREATE USER 'srbas_user'@'localhost' IDENTIFIED BY 'change-me';
   GRANT ALL PRIVILEGES ON smart_restaurant_db.* TO 'srbas_user'@'localhost';
   FLUSH PRIVILEGES;
   ```
3. Load the schema directly (or let Flask-Migrate generate it - see below):
   ```bash
   mysql -u srbas_user -p smart_restaurant_db < database/schema.sql
   ```
4. In `.env`, set:
   ```
   USE_SQLITE_FALLBACK=false
   DB_USER=srbas_user
   DB_PASSWORD=change-me
   DB_NAME=smart_restaurant_db
   ```
5. `flask seed-db` and `python run.py` as above.

### Using Alembic/Flask-Migrate instead of the raw `.sql` file

The models are the source of truth; `database/schema.sql` is a convenience
snapshot of them. To generate migrations straight from the models instead:

```bash
flask db init        # once
flask db migrate -m "initial schema"
flask db upgrade
```

---

## 3. Everyday commands

```bash
flask seed-db              # (re)populate demo data
flask backup-db            # copy the SQLite file into backups/ (for MySQL, use mysqldump on a cron/Task Scheduler instead)
pytest                     # run the test suite
pytest tests/test_billing_calculator.py -v   # just the pure billing-math tests (no DB needed)
waitress-serve --port=8000 run:app            # a slightly more "production-like" local server
```

---

## 4. Project layout

```
smart_restaurant_system/
├── run.py                     # entry point
├── config.py                  # env-driven configuration
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py             # application factory
│   ├── extensions.py           # db, login_manager, migrate, csrf
│   ├── models/                 # SQLAlchemy models
│   ├── repositories/           # Repository Pattern (data access)
│   ├── services/                # business logic (Service Layer)
│   ├── routes/                  # Flask blueprints (controllers)
│   ├── templates/               # Jinja2 + Bootstrap 5 views
│   ├── static/                  # css/js
│   └── utils/                   # decorators, validators, QR helper
├── database/
│   ├── schema.sql               # full MySQL DDL
│   └── seed.py                  # demo data generator
├── tests/
│   ├── test_billing_calculator.py  # pure logic, no DB required
│   └── test_billing_service.py     # integration tests (needs full stack)
└── docs/
    ├── ARCHITECTURE.md
    ├── ER_DIAGRAM.md
    ├── API_DESIGN.md
    ├── ROADMAP.md
    └── SPRINT_PLAN.md
```

---

## 5. Requirements

- Python 3.10+
- (Optional) A locally installed MySQL Server 8.x if you don't want the
  SQLite fallback
- No internet access needed at runtime *except* for the Bootstrap/Google
  Fonts/Plotly CDN links in `base.html` / `analytics/index.html`. If you're
  fully offline, download those assets once and point the `<link>`/`<script>`
  tags at local files instead.

## 6. Known limitations of this build

- The SQLite auto-backup is a simple file copy; for MySQL, wire up
  `mysqldump` on a system cron job / Windows Task Scheduler instead
  (`_auto_backup()` in `app/__init__.py` already logs a reminder about this).
- CSRF protection (`Flask-WTF`) is enabled globally and every POST form in
  the templates already carries a `{{ csrf_token() }}` hidden field, so this
  works out of the box - just don't add a new POST form without copying that
  same hidden input.
- See `docs/ROADMAP.md` for everything intentionally left for Phase 2.
