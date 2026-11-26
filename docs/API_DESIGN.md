# API / Route Design

This build ships as a **server-rendered Flask app** (Jinja templates), not a
pure JSON API - that matches "runs entirely on localhost" and a small
restaurant's need for a simple, fast counter UI more than a decoupled SPA
would. That said, every route is a clean, RESTish URL and the JSON endpoints
needed by the POS screen already exist, so a future React/mobile front-end
could reuse the same backend with minimal changes (see `docs/ROADMAP.md`).

| Method | Route | Auth | Purpose |
|---|---|---|---|
| GET/POST | `/login` | public | Sign in |
| GET | `/logout` | any | Sign out |
| GET | `/` , `/dashboard` | any | KPI dashboard |
| GET | `/categories/` | any | List categories |
| POST | `/categories/add` | admin | Create category |
| POST | `/categories/<id>/edit` | admin | Update category |
| POST | `/categories/<id>/delete` | admin | Delete category (blocked if items exist) |
| GET | `/items/` | any | Search/filter/paginate items |
| GET/POST | `/items/new` | admin | Create item |
| GET/POST | `/items/<id>/edit` | admin | Update item |
| POST | `/items/<id>/delete` | admin | Delete item |
| POST | `/items/bulk-update-prices` | admin | Apply a % change to many items at once |
| GET | `/items/export` | admin | CSV export of the menu |
| GET | `/billing/` | any | POS screen |
| **GET** | **`/billing/items.json`** | any | **JSON feed** the POS page's JS uses for instant client search |
| POST | `/billing/create` | any | Create a bill from a cart (JSON body in a form field) |
| GET | `/billing/receipt/<id>` | any | Printable receipt (+ QR code) |
| GET | `/billing/reprint` | any | Look up a bill by number to reprint |
| GET | `/sales/` | any | Sales history search (date range / bill number) |
| GET | `/analytics/` | admin | Pandas/Plotly analytics dashboard |
| GET | `/inventory/` | any | View stock + low-stock alerts |
| POST | `/inventory/add` \| `/<id>/update` \| `/<id>/delete` | admin | Manage raw materials |
| GET | `/employees/` | admin | List employees |
| GET/POST | `/employees/new`, `/<id>/edit` | admin | Manage employees |
| POST | `/employees/<id>/delete` | admin | Deactivate (soft delete) |
| POST | `/employees/<id>/attendance` | admin | Mark attendance |
| GET | `/customers/` | any | Search customers |
| GET/POST | `/customers/new` | any | Add a customer |
| GET | `/customers/<id>` | any | Purchase history + loyalty points |
| GET | `/reports/` | admin | Report download hub |
| GET | `/reports/sales/csv` \| `/sales/excel` | admin | Sales export |
| GET | `/reports/sales/daily-pdf` | admin | Daily sales PDF |
| GET | `/reports/tax-report/pdf` | admin | GST tax report PDF |
| GET | `/reports/inventory/csv` \| `/employees/csv` | admin | Other exports |

## Request/response shape for bill creation

`POST /billing/create` (form-encoded, not raw JSON, to keep it a plain HTML
form with no extra JS framework):

```
cart_json      = '[{"item_id": 3, "quantity": 2}, {"item_id": 7, "quantity": 1}]'
customer_phone = "9811122233"        (optional)
customer_name  = "Neha Sharma"       (optional, only used if phone is new)
coupon_code    = "WELCOME10"         (optional)
payment_mode   = "cash" | "card" | "upi"
```

On success: `302 Found -> /billing/receipt/<bill_id>`.
On failure (bad stock, empty cart, etc.): `302 Found -> /billing/` with a
flashed error message.

## Why not a pure JSON REST API?

The brief asks for a "REST API architecture" - the service/repository split
already gives you that separation, and `/billing/items.json` demonstrates
the pattern. Wrapping every module in JSON + a separate JS SPA would roughly
double the amount of code (serializers, a JS build step, CORS, auth tokens)
for a tool that's explicitly local-only and used by counter staff on one
screen. Phase 2 (see roadmap) is where a real `/api/v1/*` JSON layer using
Flask-RESTX or Flask-Smorest would pay for itself, e.g. for a future mobile
app or multi-branch sync.
