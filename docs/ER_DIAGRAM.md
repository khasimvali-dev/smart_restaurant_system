# Entity-Relationship Diagram

```mermaid
erDiagram
    EMPLOYEES ||--o{ ATTENDANCE : "has"
    EMPLOYEES ||--o| USERS : "may own"
    USERS ||--o{ BILLS : "creates (cashier)"
    CUSTOMERS ||--o{ BILLS : "places"
    COUPONS ||--o{ BILLS : "applied to"
    CATEGORIES ||--o{ ITEMS : "groups"
    BILLS ||--o{ BILL_ITEMS : "contains"
    ITEMS ||--o{ BILL_ITEMS : "sold as"

    EMPLOYEES {
        int id PK
        string name
        string role
        string phone
        decimal salary
        date joining_date
        bool is_active
    }
    ATTENDANCE {
        int id PK
        int employee_id FK
        date work_date
        string status
        time check_in
        time check_out
    }
    USERS {
        int id PK
        string username
        string full_name
        string email
        string password_hash
        enum role "admin|cashier"
        bool is_active
        int employee_id FK
    }
    CUSTOMERS {
        int id PK
        string name
        string phone
        string email
        int loyalty_points
        decimal total_spend
    }
    CATEGORIES {
        int id PK
        string name
        string description
    }
    ITEMS {
        int id PK
        string sku
        string name
        int category_id FK
        decimal price
        decimal discount_percent
        decimal tax_percent
        int quantity_available
        string status
    }
    INVENTORY {
        int id PK
        string name
        decimal quantity
        string unit
        decimal minimum_stock
    }
    COUPONS {
        int id PK
        string code
        decimal discount_percent
        decimal max_discount_amount
        date valid_from
        date valid_until
        int usage_limit
        int times_used
        bool is_active
    }
    BILLS {
        int id PK
        string bill_number
        datetime bill_date
        int cashier_id FK
        int customer_id FK
        int coupon_id FK
        decimal subtotal
        decimal discount_amount
        decimal tax_amount
        decimal grand_total
        string payment_mode
        string status
    }
    BILL_ITEMS {
        int id PK
        int bill_id FK
        int item_id FK
        string item_name_snapshot
        decimal unit_price
        int quantity
        decimal discount_percent
        decimal tax_percent
        decimal line_total
    }
```

`INVENTORY` (raw materials / ingredients) is intentionally **not** linked to
`ITEMS` with a formal recipe/BOM table in this version - see
`docs/ROADMAP.md` for the recipe-costing feature that would connect the two.

Full SQL DDL: [`database/schema.sql`](../database/schema.sql).
