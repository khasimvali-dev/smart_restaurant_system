# Roadmap

## What's included in this build (Phase 1 - working today)

- Role-based auth (Admin / Cashier), session-based login
- Full KPI dashboard (today/week/month sales, top items, low stock, recent bills)
- Category & Item management (CRUD, search, filter, bulk price update, CSV export)
- POS billing screen: cart, live discount/GST calc, coupon codes, stock check
- Printable receipt with embedded QR code, reprint-by-bill-number
- Sales history search (date range, bill number)
- Analytics dashboard: sales trend (daily/weekly/monthly/yearly), top/least
  sold items, revenue-by-category pie, peak-ordering-hours heatmap, average
  bill value, frequent customers - built with Pandas + Plotly
- Inventory (raw materials) tracking with low-stock / out-of-stock alerts
- Employee management + basic attendance marking
- Customer management with purchase history + loyalty points
- Reports: CSV, Excel, and PDF export (sales, tax, inventory, employees)
- Discount coupon system
- Dark mode toggle, keyboard shortcuts (Alt+N new bill, Alt+D dashboard, Alt+S sales)
- Local auto-backup of the SQLite file on startup / via `flask backup-db`
- Full layered architecture, MySQL schema, unit tests for the billing engine

## Phase 2 - deliberately *not* built here, and why

These items from the original brief are substantial R&D projects in their
own right. Building a shallow/fake version of them would be worse than not
including them, so they're scoped honestly instead:

| Feature | Why it's Phase 2 | What it would take |
|---|---|---|
| **Sales forecasting (ML)** | Needs a real train/validate/deploy pipeline, not a one-off script, to be trustworthy | `scikit-learn`/`Prophet`, a training job, backtesting, a model registry, a retraining schedule |
| **Demand prediction** | Same as above, plus needs recipe/BOM data (ingredients per dish) that doesn't exist yet | Recipe table linking `items` <-> `inventory`, historical consumption data, a forecasting model |
| **Item recommendation engine** | Needs meaningfully more order history than a new restaurant has on day one, or it just recommends the top sellers | Collaborative filtering or association-rule mining (`mlxtend` apriori) once there's real transaction volume |
| **Barcode generation & scanning** | Generating a barcode image is easy (`python-barcode`, already in requirements.txt) - the real barcode *workflow* (label printer templates, USB/Bluetooth scanner integration, SKU lookup on scan) needs actual hardware to design and test against | A physical barcode scanner + label printer for integration testing |
| **Multi-branch ERP** | Changes the data model (every table needs `branch_id`), changes auth (branch-scoped roles), changes reporting (consolidated vs per-branch) - a schema migration, not a feature flag | A `branches` table, `branch_id` FK across `bills`/`items`/`inventory`/`employees`, branch-scoped queries everywhere, a "head office" consolidated view |
| **Seasonal sales analysis** | Statistically meaningless without 2+ years of data (a single restaurant's first year has no "same season last year" to compare against) | Wait for real historical data, then add a year-over-year comparison view (the `analytics_service.py` groupby structure already supports adding this later) |
| **Profit & Loss analytics** | Needs a costing model (ingredient cost per dish, staff cost allocation, overhead) that doesn't exist in the current schema | A `recipe_cost` table, expense tracking, allocation rules |

## Suggested build order for Phase 2

1. Recipe/BOM table (`recipe_items`: item_id, inventory_id, quantity_used) -
   this single addition unlocks demand prediction, P&L, and automatic
   inventory deduction on every sale.
2. `/api/v1/*` JSON layer (Flask-RESTX) once a mobile app or kiosk is planned.
3. Barcode/QR *scanning* (not just generation) once a scanner is available to test with.
4. Multi-branch schema migration, once there's a second physical location.
5. ML forecasting, once at least 6-12 months of real sales data exists to train on.
