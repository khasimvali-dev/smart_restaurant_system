"""
Integration-level tests exercising BillingService against a real (in-memory
SQLite) database. Requires the full requirements.txt to be installed -
run with:  pytest tests/test_billing_service.py -v
"""
from datetime import date
from app.models.category import Category
from app.models.item import Item
from app.models.user import User, RoleEnum
from app.services.billing_service import BillingService, InsufficientStockError


def _make_cashier(db):
    user = User(username="testcashier", full_name="Test Cashier", role=RoleEnum.CASHIER)
    user.set_password("pass1234")
    db.session.add(user)
    db.session.commit()
    return user


def _make_item(db, name="Tea", price=40, qty=10, discount=0, tax=5):
    category = Category(name="Beverages")
    db.session.add(category)
    db.session.flush()
    item = Item(
        sku=f"SKU-{name}", name=name, category_id=category.id, price=price,
        discount_percent=discount, tax_percent=tax, quantity_available=qty, status="available",
    )
    db.session.add(item)
    db.session.commit()
    return item


def test_create_bill_happy_path(app, db):
    cashier = _make_cashier(db)
    item = _make_item(db, qty=10)
    service = BillingService()

    bill = service.create_bill(cashier_id=cashier.id, cart=[{"item_id": item.id, "quantity": 2}])

    assert bill.id is not None
    assert bill.line_items[0].quantity == 2
    assert float(bill.grand_total) > 0
    # stock should be decremented
    assert item.quantity_available == 8


def test_create_bill_insufficient_stock_raises(app, db):
    cashier = _make_cashier(db)
    item = _make_item(db, qty=1)
    service = BillingService()

    try:
        service.create_bill(cashier_id=cashier.id, cart=[{"item_id": item.id, "quantity": 5}])
        assert False, "expected InsufficientStockError"
    except InsufficientStockError:
        pass


def test_create_bill_empty_cart_raises(app, db):
    cashier = _make_cashier(db)
    service = BillingService()
    try:
        service.create_bill(cashier_id=cashier.id, cart=[])
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_bill_number_increments_per_day(app, db):
    cashier = _make_cashier(db)
    item = _make_item(db, qty=50)
    service = BillingService()

    bill1 = service.create_bill(cashier_id=cashier.id, cart=[{"item_id": item.id, "quantity": 1}])
    bill2 = service.create_bill(cashier_id=cashier.id, cart=[{"item_id": item.id, "quantity": 1}])

    assert bill1.bill_number != bill2.bill_number
    assert bill1.bill_number.endswith("0001")
    assert bill2.bill_number.endswith("0002")
