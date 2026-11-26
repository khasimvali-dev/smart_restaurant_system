-- ============================================================================
-- Smart Restaurant Billing & Analytics System
-- MySQL Schema  |  Engine: InnoDB  |  Charset: utf8mb4
--
-- Table creation order (dependency chain):
--   1. employees          – no foreign keys
--   2. attendance         – depends on employees
--   3. users              – depends on employees
--   4. customers          – no foreign keys
--   5. categories         – no foreign keys
--   6. items              – depends on categories
--   7. inventory          – no foreign keys
--   8. coupons            – no foreign keys
--   9. bills              – depends on users, customers, coupons
--  10. bill_items         – depends on bills, items
--
-- Usage:
--   mysql -u root -p -e "CREATE DATABASE smart_restaurant_db CHARACTER SET utf8mb4;"
--   mysql -u root -p smart_restaurant_db < database/schema.sql
--
-- Alternatively, let Flask-Migrate generate the schema automatically:
--   flask db upgrade
-- ============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================================
-- 1. EMPLOYEES
--    Core staff table. Referenced by attendance and users.
-- ============================================================================
CREATE TABLE IF NOT EXISTS employees (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    name            VARCHAR(120)    NOT NULL,
    role            VARCHAR(60)     NOT NULL,                       -- e.g. Chef, Waiter, Manager
    phone           VARCHAR(20)     NOT NULL,
    salary          DECIMAL(10,2)   NOT NULL        DEFAULT 0,
    joining_date    DATE            NOT NULL,
    is_active       BOOLEAN         NOT NULL        DEFAULT TRUE,
    created_at      DATETIME        NOT NULL        DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 2. ATTENDANCE
--    Daily attendance log per employee. One record per employee per day.
-- ============================================================================
CREATE TABLE IF NOT EXISTS attendance (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    employee_id     INT             NOT NULL,
    work_date       DATE            NOT NULL,
    status          VARCHAR(20)     NOT NULL        DEFAULT 'present',  -- present / absent / leave
    check_in        TIME                            NULL,
    check_out       TIME                            NULL,

    UNIQUE KEY uq_employee_date (employee_id, work_date),

    CONSTRAINT fk_attendance_employee
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 3. USERS
--    System login accounts. Optionally linked to an employee record.
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    username        VARCHAR(80)     NOT NULL        UNIQUE,
    full_name       VARCHAR(120)    NOT NULL,
    email           VARCHAR(150)                    UNIQUE NULL,
    password_hash   VARCHAR(255)    NOT NULL,
    role            ENUM('admin','cashier')
                                    NOT NULL        DEFAULT 'cashier',
    is_active       BOOLEAN         NOT NULL        DEFAULT TRUE,
    employee_id     INT                             NULL,
    created_at      DATETIME        NOT NULL        DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_users_username (username),

    CONSTRAINT fk_users_employee
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 4. CUSTOMERS
--    Walk-in or registered customers with loyalty tracking.
-- ============================================================================
CREATE TABLE IF NOT EXISTS customers (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    name            VARCHAR(120)    NOT NULL,
    phone           VARCHAR(20)     NOT NULL        UNIQUE,
    email           VARCHAR(150)                    NULL,
    loyalty_points  INT             NOT NULL        DEFAULT 0,
    total_spend     DECIMAL(12,2)   NOT NULL        DEFAULT 0,
    created_at      DATETIME        NOT NULL        DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_customers_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 5. CATEGORIES
--    Menu item groupings (e.g. Starters, Mains, Beverages).
-- ============================================================================
CREATE TABLE IF NOT EXISTS categories (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    name            VARCHAR(80)     NOT NULL        UNIQUE,
    description     VARCHAR(255)                    NULL,
    created_at      DATETIME        NOT NULL        DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 6. ITEMS
--    Menu items / products available for sale.
-- ============================================================================
CREATE TABLE IF NOT EXISTS items (
    id                  INT             AUTO_INCREMENT  PRIMARY KEY,
    sku                 VARCHAR(30)     NOT NULL        UNIQUE,         -- human-readable item code
    name                VARCHAR(120)    NOT NULL,
    category_id         INT             NOT NULL,
    price               DECIMAL(10,2)   NOT NULL,
    discount_percent    DECIMAL(5,2)    NOT NULL        DEFAULT 0,
    tax_percent         DECIMAL(5,2)    NOT NULL        DEFAULT 5.00,
    quantity_available  INT             NOT NULL        DEFAULT 0,
    status              VARCHAR(15)     NOT NULL        DEFAULT 'available',  -- available / unavailable
    image_filename      VARCHAR(255)                    NULL,
    created_at          DATETIME        NOT NULL        DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME        NOT NULL        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_items_name (name),
    INDEX idx_items_sku  (sku),

    CONSTRAINT fk_items_category
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 7. INVENTORY
--    Raw ingredient / supply stock levels.
-- ============================================================================
CREATE TABLE IF NOT EXISTS inventory (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    name            VARCHAR(120)    NOT NULL        UNIQUE,
    quantity        DECIMAL(10,2)   NOT NULL        DEFAULT 0,
    unit            VARCHAR(20)     NOT NULL        DEFAULT 'kg',      -- kg, litre, pcs, …
    minimum_stock   DECIMAL(10,2)   NOT NULL        DEFAULT 0,
    created_at      DATETIME        NOT NULL        DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 8. COUPONS
--    Discount codes with validity window and optional usage cap.
-- ============================================================================
CREATE TABLE IF NOT EXISTS coupons (
    id                  INT             AUTO_INCREMENT  PRIMARY KEY,
    code                VARCHAR(30)     NOT NULL        UNIQUE,
    discount_percent    DECIMAL(5,2)    NOT NULL,
    max_discount_amount DECIMAL(10,2)                   NULL,          -- cap in currency; NULL = no cap
    valid_from          DATE            NOT NULL,
    valid_until         DATE            NOT NULL,
    usage_limit         INT                             NULL,          -- NULL = unlimited
    times_used          INT             NOT NULL        DEFAULT 0,
    is_active           BOOLEAN         NOT NULL        DEFAULT TRUE,
    created_at          DATETIME        NOT NULL        DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME        NOT NULL        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_coupons_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 9. BILLS
--    Transaction header. Each bill is raised by a cashier (user).
-- ============================================================================
CREATE TABLE IF NOT EXISTS bills (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    bill_number     VARCHAR(30)     NOT NULL        UNIQUE,
    bill_date       DATETIME        NOT NULL        DEFAULT CURRENT_TIMESTAMP,
    cashier_id      INT             NOT NULL,
    customer_id     INT                             NULL,
    coupon_id       INT                             NULL,
    subtotal        DECIMAL(12,2)   NOT NULL        DEFAULT 0,
    discount_amount DECIMAL(12,2)   NOT NULL        DEFAULT 0,
    tax_amount      DECIMAL(12,2)   NOT NULL        DEFAULT 0,
    grand_total     DECIMAL(12,2)   NOT NULL        DEFAULT 0,
    payment_mode    VARCHAR(20)     NOT NULL        DEFAULT 'cash',    -- cash / card / upi
    status          VARCHAR(20)     NOT NULL        DEFAULT 'completed',  -- completed / void
    created_at      DATETIME        NOT NULL        DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_bills_bill_number (bill_number),
    INDEX idx_bills_bill_date   (bill_date),

    CONSTRAINT fk_bills_cashier
        FOREIGN KEY (cashier_id)  REFERENCES users(id)      ON DELETE RESTRICT,
    CONSTRAINT fk_bills_customer
        FOREIGN KEY (customer_id) REFERENCES customers(id)  ON DELETE SET NULL,
    CONSTRAINT fk_bills_coupon
        FOREIGN KEY (coupon_id)   REFERENCES coupons(id)    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 10. BILL_ITEMS
--     Line items within a bill. Snapshots item name/price at time of sale.
-- ============================================================================
CREATE TABLE IF NOT EXISTS bill_items (
    id                  INT             AUTO_INCREMENT  PRIMARY KEY,
    bill_id             INT             NOT NULL,
    item_id             INT             NOT NULL,
    item_name_snapshot  VARCHAR(120)    NOT NULL,                      -- preserved if item edited later
    unit_price          DECIMAL(10,2)   NOT NULL,
    quantity            INT             NOT NULL        DEFAULT 1,
    discount_percent    DECIMAL(5,2)    NOT NULL        DEFAULT 0,
    tax_percent         DECIMAL(5,2)    NOT NULL        DEFAULT 0,
    line_total          DECIMAL(12,2)   NOT NULL,

    CONSTRAINT fk_bill_items_bill
        FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE,
    CONSTRAINT fk_bill_items_item
        FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
SET FOREIGN_KEY_CHECKS = 1;
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Entity Relationships (see docs/ER_DIAGRAM.md for the full diagram)
-- ----------------------------------------------------------------------------
--
--  employees  (1) ──── (*)  attendance       cascade delete
--  employees  (1) ──── (0,1) users           set null on delete
--  categories (1) ──── (*)  items            restrict delete
--  users      (1) ──── (*)  bills            restrict delete  [cashier]
--  customers  (1) ──── (*)  bills            set null on delete
--  coupons    (1) ──── (*)  bills            set null on delete
--  bills      (1) ──── (*)  bill_items       cascade delete
--  items      (1) ──── (*)  bill_items       restrict delete
--
-- ----------------------------------------------------------------------------
