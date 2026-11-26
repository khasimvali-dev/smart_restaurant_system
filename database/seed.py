"""
Populate the database with realistic demo data so every module - dashboard,
billing, analytics, inventory alerts - has something to show immediately.

Run with:  flask seed-db
"""
import random
from datetime import date, datetime, timedelta

from app.extensions import db
from app.models.user import User, RoleEnum
from app.models.employee import Employee
from app.models.customer import Customer
from app.models.category import Category
from app.models.item import Item
from app.models.inventory import InventoryItem
from app.models.coupon import Coupon
from app.services.billing_service import BillingService

CATEGORY_ITEMS = {
    "Starters": [
        ("Paneer Tikka", 220, 15), ("Veg Spring Rolls", 160, 20),
        ("Chicken 65", 240, 18), ("Corn Cheese Balls", 180, 25),
    ],
    "Main Course": [
        ("Butter Chicken", 320, 20), ("Paneer Butter Masala", 280, 22),
        ("Masala Dosa", 130, 30), ("Veg Biryani", 210, 25), ("Chicken Biryani", 260, 20),
    ],
    "Desserts": [
        ("Gulab Jamun (2 pc)", 90, 15), ("Chocolate Brownie", 150, 12),
        ("Rasmalai (2 pc)", 110, 10),
    ],
    "Beverages": [
        ("Masala Chai", 40, 40), ("Cold Coffee", 110, 30), ("Fresh Lime Soda", 70, 35),
        ("Mango Lassi", 100, 25),
    ],
    "Ice Creams": [
        ("Vanilla Scoop", 60, 20), ("Chocolate Sundae", 150, 15),
    ],
}

INVENTORY_SEED = [
    ("Basmati Rice", 40, "kg", 10), ("Paneer", 15, "kg", 5), ("Chicken", 25, "kg", 8),
    ("Tomatoes", 8, "kg", 10),   # intentionally below minimum -> low stock demo
    ("Milk", 20, "litre", 15), ("Cooking Oil", 30, "litre", 10),
    ("Sugar", 2, "kg", 5),       # intentionally below minimum -> low stock demo
]


def run_seed():
    db.create_all()

    # --- Categories & Items ------------------------------------------------
    categories = {}
    for name in CATEGORY_ITEMS:
        cat = Category.query.filter_by(name=name).first()
        if not cat:
            cat = Category(name=name, description=f"{name} menu section")
            db.session.add(cat)
            db.session.flush()
        categories[name] = cat

    sku_counter = 1
    items_created = []
    for cat_name, entries in CATEGORY_ITEMS.items():
        for item_name, price, tax in entries:
            existing = Item.query.filter_by(name=item_name).first()
            if existing:
                items_created.append(existing)
                continue
            item = Item(
                sku=f"ITM-{sku_counter:04d}",
                name=item_name,
                category_id=categories[cat_name].id,
                price=price,
                discount_percent=random.choice([0, 0, 5, 10]),
                tax_percent=5.0,
                quantity_available=random.randint(20, 80),
                status="available",
            )
            sku_counter += 1
            db.session.add(item)
            items_created.append(item)
    db.session.flush()

    # --- Inventory -----------------------------------------------------------
    for name, qty, unit, min_stock in INVENTORY_SEED:
        if not InventoryItem.query.filter_by(name=name).first():
            db.session.add(InventoryItem(name=name, quantity=qty, unit=unit, minimum_stock=min_stock))

    # --- Employees & Users ---------------------------------------------------
    admin_employee = Employee.query.filter_by(name="Asha Rao").first()
    if not admin_employee:
        admin_employee = Employee(
            name="Asha Rao", role="Manager", phone="9900011122",
            salary=45000, joining_date=date(2024, 1, 10),
        )
        db.session.add(admin_employee)
        db.session.flush()

    cashier_employee = Employee.query.filter_by(name="Ravi Kumar").first()
    if not cashier_employee:
        cashier_employee = Employee(
            name="Ravi Kumar", role="Cashier", phone="9900022233",
            salary=22000, joining_date=date(2024, 6, 1),
        )
        db.session.add(cashier_employee)
        db.session.flush()

    from app.services.auth_service import AuthService
    auth_service = AuthService()

    if not User.query.filter_by(username="admin").first():
        auth_service.create_user(
            username="admin", full_name="Asha Rao", password="Admin@123",
            role=RoleEnum.ADMIN, email="admin@smartrestaurant.local",
            employee_id=admin_employee.id,
        )
    if not User.query.filter_by(username="cashier").first():
        auth_service.create_user(
            username="cashier", full_name="Ravi Kumar", password="Cashier@123",
            role=RoleEnum.CASHIER, email="cashier@smartrestaurant.local",
            employee_id=cashier_employee.id,
        )

    # --- Customers -------------------------------------------------------
    demo_customers = [
        ("Neha Sharma", "9811122233", "neha@example.com"),
        ("Arjun Mehta", "9822233344", "arjun@example.com"),
        ("Priya Nair", "9833344455", "priya@example.com"),
    ]
    for name, phone, email in demo_customers:
        if not Customer.query.filter_by(phone=phone).first():
            db.session.add(Customer(name=name, phone=phone, email=email))

    # --- Coupons -----------------------------------------------------------
    if not Coupon.query.filter_by(code="WELCOME10").first():
        db.session.add(Coupon(
            code="WELCOME10", discount_percent=10, max_discount_amount=100,
            valid_from=date.today() - timedelta(days=30),
            valid_until=date.today() + timedelta(days=180),
            usage_limit=None,
        ))

    db.session.commit()

    # --- Sample bill history (last 30 days) so analytics has data ------------
    if Item.query.count() and User.query.count():
        _generate_sample_bills()

    # Replenish menu item stock so POS billing can be tested immediately
    for item in Item.query.all():
        item.quantity_available = random.randint(35, 80)
        item.status = "available"
    db.session.commit()


def _generate_sample_bills(days=30, bills_per_day_range=(3, 9)):
    from app.models.bill import Bill

    if Bill.query.count() > 0:
        return  # don't duplicate on re-seed

    cashier = User.query.filter_by(username="cashier").first() or User.query.first()
    items = Item.query.all()
    billing_service = BillingService()

    for day_offset in range(days, 0, -1):
        day = datetime.utcnow() - timedelta(days=day_offset)
        num_bills = random.randint(*bills_per_day_range)
        for _ in range(num_bills):
            chosen_items = random.sample(items, k=random.randint(1, 4))
            cart = [{"item_id": i.id, "quantity": random.randint(1, 3)} for i in chosen_items]
            try:
                bill = billing_service.create_bill(
                    cashier_id=cashier.id, cart=cart, payment_mode=random.choice(["cash", "card", "upi"])
                )
                # backdate the bill for realistic historical trends
                random_hour = random.randint(9, 22)
                bill.bill_date = day.replace(hour=random_hour, minute=random.randint(0, 59))
            except Exception:
                continue
        db.session.commit()
