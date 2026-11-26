# Architecture

## Layered / Clean Architecture

The codebase follows a strict **4-layer** structure so business logic never
touches HTTP or SQL directly:

```
Routes (Controllers)   ->  Flask Blueprints. Parse request, call a Service, render a template.
        |
Services                ->  Business rules. Validation, orchestration, calculations.
        |                   No Flask imports. Depend only on Repositories + Models.
Repositories            ->  Data access. One class per aggregate root. All queries live here.
        |
Models (SQLAlchemy ORM) ->  Table definitions + simple computed properties only.
```

Why this matters in practice:

* **Testability** - `app/services/billing_calculator.py` has *zero* Flask/DB
  imports, so the entire pricing engine (discounts, GST, coupon capping) is
  unit-tested in isolation (`tests/test_billing_calculator.py`) without a
  database or a running server.
* **Swappable persistence** - Repositories are the only place that talks
  SQLAlchemy. Swapping MySQL for Postgres, or adding a caching layer, only
  touches the repository layer.
* **Swappable transport** - Because services don't import `flask`, the same
  `BillingService` could be reused by a future CLI tool, a Celery task, or a
  REST API without change.

## Request lifecycle example: creating a bill

1. `POST /billing/create` hits `billing_routes.create_bill`.
2. The route parses the posted cart JSON and coupon code, then calls
   `BillingService.create_bill(...)`.
3. `BillingService`:
   - looks up each `Item`, checks `is_available` / stock,
   - delegates all money math to the pure `billing_calculator.calculate_bill()`,
   - persists `Bill` + `BillItem` rows and decrements stock, in one transaction,
   - updates the customer's loyalty points if a phone number was given.
4. The route redirects to `/billing/receipt/<id>`, which renders a printable
   receipt (with an embedded QR code generated on the fly).

## Design Patterns Used

| Pattern | Where |
|---|---|
| Application Factory | `app/__init__.py::create_app()` |
| Repository Pattern | `app/repositories/*` |
| Service Layer | `app/services/*` |
| Strategy-ish calculator | `billing_calculator.py` (pure functions, no state) |
| Mixin | `app/models/mixins.py` (`TimestampMixin`, `SoftDeleteMixin`) |
| Decorator (RBAC) | `app/utils/decorators.py::roles_required` |
| Blueprint / MVC | `app/routes/*` + `app/templates/*` |
| DTO-ish dataclasses | `LineItemInput` / `LineItemResult` / `BillCalculationResult` |

## Environment Configuration

Everything environment-specific (DB engine, secrets, restaurant details,
GST rate, backup schedule) is read from `.env` via `config.py` - never
hard-coded. The same code runs against:

* **SQLite** (`USE_SQLITE_FALLBACK=true`) - zero external services, perfect
  for a first run or a demo.
* **MySQL** (`USE_SQLITE_FALLBACK=false`) - the real local production target,
  connected via the pure-Python `PyMySQL` driver so no system `libmysqlclient`
  needs to be compiled/installed.

## Logging & Error Handling

* Rotating file logs at `logs/app.log` (`RotatingFileHandler`, 1MB x 5 files).
* Global 403 / 404 / 500 error pages (`app/templates/errors/`).
* Every service method raises plain `ValueError` / a small number of custom
  exceptions (e.g. `InsufficientStockError`) - routes catch these and turn
  them into flash messages, so the user never sees a raw stack trace.

## Multi-branch readiness (documented, not built)

The schema and services are intentionally written so a `branch_id` column
could be added to `bills`, `items`, and `inventory` later without a rewrite -
see `docs/ROADMAP.md` for what a Phase 2 multi-branch ERP upgrade would
involve.
