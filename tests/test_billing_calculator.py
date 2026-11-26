"""
These tests exercise the pure billing math in app/services/billing_calculator.py
and have zero DB/Flask dependency, so `pytest tests/test_billing_calculator.py`
works even before SQLAlchemy/MySQL are installed.
"""
import pytest
from app.services.billing_calculator import LineItemInput, calculate_bill, calculate_line_item


def test_single_line_item_no_discount_no_tax():
    line = LineItemInput(item_id=1, name="Tea", unit_price=40, quantity=2)
    result = calculate_line_item(line)
    assert result.gross_amount == 80.0
    assert result.discount_amount == 0.0
    assert result.tax_amount == 0.0
    assert result.line_total == 80.0


def test_single_line_item_with_discount_and_tax():
    line = LineItemInput(item_id=1, name="Biryani", unit_price=250, quantity=2, discount_percent=10, tax_percent=5)
    result = calculate_line_item(line)
    assert result.gross_amount == 500.0
    assert result.discount_amount == 50.0
    assert result.taxable_amount == 450.0
    assert result.tax_amount == 22.5
    assert result.line_total == 472.5


def test_zero_quantity_raises():
    with pytest.raises(ValueError):
        calculate_line_item(LineItemInput(item_id=1, name="X", unit_price=10, quantity=0))


def test_negative_price_raises():
    with pytest.raises(ValueError):
        calculate_line_item(LineItemInput(item_id=1, name="X", unit_price=-5, quantity=1))


def test_full_bill_multiple_items_with_coupon():
    lines = [
        LineItemInput(item_id=1, name="Paneer Tikka", unit_price=250, quantity=2, discount_percent=10, tax_percent=5),
        LineItemInput(item_id=2, name="Masala Dosa", unit_price=120, quantity=3, discount_percent=0, tax_percent=5),
    ]
    result = calculate_bill(lines, coupon_discount_percent=5, coupon_max_discount=50)
    assert result.subtotal == 860.0
    assert result.total_tax == 40.5
    # 5% of taxable_total(810) = 40.5, under the 50 cap, so it applies in full
    assert result.coupon_discount == 40.5
    assert result.grand_total == 810.0


def test_coupon_discount_is_capped():
    lines = [LineItemInput(item_id=1, name="Big Thali", unit_price=1000, quantity=1, tax_percent=5)]
    # 20% of 1000 = 200, but capped at 75
    result = calculate_bill(lines, coupon_discount_percent=20, coupon_max_discount=75)
    assert result.coupon_discount == 75.0
    assert result.grand_total == pytest.approx(1000 + 50 - 75)  # taxable + tax - capped discount


def test_empty_cart_raises():
    with pytest.raises(ValueError):
        calculate_bill([])
