-- ============================================================================
-- Smart Restaurant Billing & Analytics System
-- Full MySQL schema (InnoDB, utf8mb4). Mirrors the SQLAlchemy models in
-- app/models/*.py exactly - use this file for a from-scratch MySQL install,
-- or let `flask db upgrade` (Alembic/Flask-Migrate) generate an equivalent
-- schema automatically from the models instead.
--
-- Usage:
--   mysql -u root -p -e "CREATE DATABASE smart_restaurant_db CHARACTER SET utf8mb4;"
--   mysql -u root -p smart_restaurant_db < database/schema.sql
-- ============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ---------------------------------------------------------------- employees
CREATE TABLE IF NOT EXISTS employees (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(120) NOT NULL,
    role            VARCHAR(60)  NOT NULL,
    phone           VARCHAR(20)  NOT NULL,
    salary          DECIMAL(10,2) NOT NULL DEFAULT 0,
    joining_date    DATE NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- --------------------------------------------------------------- attendance
CREATE TABLE IF NOT EXISTS attendance (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    employee_id     INT NOT NULL,
    work_date       DATE NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'present',
    check_in        TIME NULL,
    check_out       TIME NULL,
    UNIQUE KEY uq_employee_date (employee_id, work_date),
    CONSTRAINT fk_attendance_employee FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------------------- users
CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(80)  NOT NULL UNIQUE,
    full_name       VARCHAR(120) NOT NULL,
    email           VARCHAR(150) UNIQUE NULL,
    password_hash   VARCHAR(255) NOT NULL,
    role            ENUM('admin','cashier') NOT NULL DEFAULT 'cashier',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    employee_id     INT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_employee FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL,
    INDEX idx_users_username (username)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------- customers
CREATE TABLE IF NOT EXISTS customers (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(120) NOT NULL,
    phone           VARCHAR(20)  NOT NULL UNIQUE,
    email           VARCHAR(150) NULL,
    loyalty_points  INT NOT NULL DEFAULT 0,
    total_spend     DECIMAL(12,2) NOT NULL DEFAULT 0,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_customers_phone (phone)
) ENGINE=InnoDB;

-- --------------------------------------------------------------- categories
CREATE TABLE IF NOT EXISTS categories (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(80) NOT NULL UNIQUE,
    description     VARCHAR(255) NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- -------------------------------------------------------------------- items
CREATE TABLE IF NOT EXISTS items (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    sku                 VARCHAR(30)  NOT NULL UNIQUE,
    name                VARCHAR(120) NOT NULL,
    category_id         INT NOT NULL,
    price               DECIMAL(10,2) NOT NULL,
    discount_percent    DECIMAL(5,2) NOT NULL DEFAULT 0,
    tax_percent         DECIMAL(5,2) NOT NULL DEFAULT 5.00,
    quantity_available  INT NOT NULL DEFAULT 0,
    status              VARCHAR(15) NOT NULL DEFAULT 'available',
    image_filename      VARCHAR(255) NULL,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_items_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    INDEX idx_items_name (name),
    INDEX idx_items_sku (sku)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------- inventory
CREATE TABLE IF NOT EXISTS inventory (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(120) NOT NULL UNIQUE,
    quantity        DECIMAL(10,2) NOT NULL DEFAULT 0,
    unit            VARCHAR(20)  NOT NULL DEFAULT 'kg',
    minimum_stock   DECIMAL(10,2) NOT NULL DEFAULT 0,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------------ coupons
CREATE TABLE IF NOT EXISTS coupons (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    code                    VARCHAR(30) NOT NULL UNIQUE,
    discount_percent        DECIMAL(5,2) NOT NULL,
    max_discount_amount     DECIMAL(10,2) NULL,
    valid_from              DATE NOT NULL,
    valid_until             DATE NOT NULL,
    usage_limit             INT NULL,
    times_used              INT NOT NULL DEFAULT 0,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_coupons_code (code)
) ENGINE=InnoDB;

-- --------------------------------------------------------------------- bills
CREATE TABLE IF NOT EXISTS bills (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    bill_number         VARCHAR(30) NOT NULL UNIQUE,
    bill_date           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cashier_id          INT NOT NULL,
    customer_id         INT NULL,
    coupon_id           INT NULL,
    subtotal            DECIMAL(12,2) NOT NULL DEFAULT 0,
    discount_amount     DECIMAL(12,2) NOT NULL DEFAULT 0,
    tax_amount          DECIMAL(12,2) NOT NULL DEFAULT 0,
    grand_total         DECIMAL(12,2) NOT NULL DEFAULT 0,
    payment_mode        VARCHAR(20) NOT NULL DEFAULT 'cash',
    status              VARCHAR(20) NOT NULL DEFAULT 'completed',
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_bills_cashier  FOREIGN KEY (cashier_id)  REFERENCES users(id)     ON DELETE RESTRICT,
    CONSTRAINT fk_bills_customer FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    CONSTRAINT fk_bills_coupon   FOREIGN KEY (coupon_id)   REFERENCES coupons(id)   ON DELETE SET NULL,
    INDEX idx_bills_bill_number (bill_number),
    INDEX idx_bills_bill_date (bill_date)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------- bill_items
CREATE TABLE IF NOT EXISTS bill_items (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    bill_id             INT NOT NULL,
    item_id             INT NOT NULL,
    item_name_snapshot  VARCHAR(120) NOT NULL,
    unit_price          DECIMAL(10,2) NOT NULL,
    quantity            INT NOT NULL DEFAULT 1,
    discount_percent    DECIMAL(5,2) NOT NULL DEFAULT 0,
    tax_percent         DECIMAL(5,2) NOT NULL DEFAULT 0,
    line_total          DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_bill_items_bill FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE,
    CONSTRAINT fk_bill_items_item FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- Notes on relationships (see docs/ER_DIAGRAM.md for the full diagram):
--   employees (1) ---- (0..1) users            [a user account may link to one employee]
--   employees (1) ---- (*)   attendance
--   categories (1) ---- (*)  items
--   users (1)      ---- (*)  bills              [cashier who created the bill]
--   customers (1)  ---- (*)  bills
--   coupons (1)    ---- (*)  bills
--   bills (1)      ---- (*)  bill_items
--   items (1)      ---- (*)  bill_items
-- ============================================================================
