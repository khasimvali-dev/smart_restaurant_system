# Development Roadmap, Sprint Plan & Feature Priority Matrix

## Feature Priority Matrix

| Priority | Feature | Impact | Effort | Status |
|---|---|---|---|---|
| P0 | Auth + roles | High | Low | ✅ Done |
| P0 | Item & Category management | High | Low | ✅ Done |
| P0 | Billing / POS + receipt | High | Medium | ✅ Done |
| P0 | Sales history search | High | Low | ✅ Done |
| P1 | Dashboard KPIs | High | Low | ✅ Done |
| P1 | Inventory + low-stock alerts | Medium | Low | ✅ Done |
| P1 | Reports (CSV/Excel/PDF) | Medium | Medium | ✅ Done |
| P2 | Analytics dashboard (Pandas/Plotly) | Medium | Medium | ✅ Done |
| P2 | Employee + Customer management | Medium | Low | ✅ Done |
| P2 | Coupons + Loyalty points | Low-Medium | Low | ✅ Done |
| P2 | QR receipts, dark mode, shortcuts | Low | Low | ✅ Done |
| P3 | Barcode label workflow (hardware) | Low (until scaling) | High | 🔜 Phase 2 |
| P3 | Sales forecasting (ML) | Medium (later) | High | 🔜 Phase 2 |
| P3 | Recommendation engine | Low (until volume) | Medium | 🔜 Phase 2 |
| P4 | Multi-branch ERP | Low (single site today) | Very High | 🔜 Phase 2 |
| P4 | Profit & Loss / recipe costing | Medium | High | 🔜 Phase 2 |

## Sprint Plan (as actually built)

**Sprint 0 - Foundations**
Project skeleton, config/env handling, logging, DB models, MySQL schema, repository base class.

**Sprint 1 - Core catalog & auth**
Users/roles, login/logout, Category CRUD, Item CRUD + search/filter/bulk price update.

**Sprint 2 - Billing core**
Pure billing calculator (unit tested first), BillingService, POS screen + cart JS,
receipt template + QR code, reprint lookup, sales history search.

**Sprint 3 - Operations**
Inventory tracking + alerts, Employee management + attendance, Customer
management + loyalty points, Coupon system.

**Sprint 4 - Analytics & reporting**
Pandas aggregation functions, Plotly charts (trend/top-items/category/heatmap),
analytics dashboard page, CSV/Excel/PDF report generation.

**Sprint 5 - Polish**
Dark mode, keyboard shortcuts, auto-backup, error pages, documentation,
ER diagram, roadmap, this sprint plan.

## Suggested Next Sprints (Phase 2, for the team to plan when ready)

**Sprint 6** - Recipe/BOM table + automatic ingredient deduction on sale.
**Sprint 7** - JSON API layer (`/api/v1`) for a future mobile/kiosk client.
**Sprint 8** - Real barcode scanner integration (needs hardware).
**Sprint 9** - Multi-branch schema migration + branch-scoped reporting.
**Sprint 10** - ML sales forecasting, once 6-12 months of real data exists.
