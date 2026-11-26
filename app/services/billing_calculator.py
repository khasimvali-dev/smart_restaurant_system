"""
Pure calculation functions for the billing engine.

Deliberately free of any Flask / SQLAlchemy import so it can be unit
tested in isolation (see tests/test_billing_service.py) and reused by
the receipt renderer, the API, and the analytics module alike.
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP


def _round(value) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


@dataclass
class LineItemInput:
    item_id: int
    name: str
    unit_price: float
    quantity: int
    discount_percent: float = 0.0
    tax_percent: float = 0.0


@dataclass
class LineItemResult:
    item_id: int
    name: str
    unit_price: float
    quantity: int
    discount_percent: float
    tax_percent: float
    gross_amount: float       # unit_price * qty, before discount/tax
    discount_amount: float
    taxable_amount: float     # gross - discount
    tax_amount: float
    line_total: float         # taxable_amount + tax_amount


@dataclass
class BillCalculationResult:
    line_items: list = field(default_factory=list)
    subtotal: float = 0.0          # sum of gross amounts
    total_discount: float = 0.0    # line discounts + bill-level coupon discount
    total_tax: float = 0.0
    grand_total: float = 0.0
    coupon_discount: float = 0.0


def calculate_line_item(line: LineItemInput) -> LineItemResult:
    if line.quantity <= 0:
        raise ValueError(f"Quantity for '{line.name}' must be greater than zero.")
    if line.unit_price < 0:
        raise ValueError(f"Unit price for '{line.name}' cannot be negative.")

    gross_amount = _round(line.unit_price * line.quantity)
    discount_amount = _round(gross_amount * (line.discount_percent / 100))
    taxable_amount = _round(gross_amount - discount_amount)
    tax_amount = _round(taxable_amount * (line.tax_percent / 100))
    line_total = _round(taxable_amount + tax_amount)

    return LineItemResult(
        item_id=line.item_id,
        name=line.name,
        unit_price=line.unit_price,
        quantity=line.quantity,
        discount_percent=line.discount_percent,
        tax_percent=line.tax_percent,
        gross_amount=gross_amount,
        discount_amount=discount_amount,
        taxable_amount=taxable_amount,
        tax_amount=tax_amount,
        line_total=line_total,
    )


def calculate_bill(
    lines: list[LineItemInput],
    coupon_discount_percent: float = 0.0,
    coupon_max_discount: float | None = None,
) -> BillCalculationResult:
    """
    Compute a full bill: every line item's discount + tax, then apply an
    optional bill-level coupon discount on top of the (already item-discounted)
    subtotal, before final tax has been baked into each line.
    """
    if not lines:
        raise ValueError("A bill must contain at least one line item.")

    computed_lines = [calculate_line_item(line) for line in lines]

    subtotal = _round(sum(l.gross_amount for l in computed_lines))
    line_discounts = _round(sum(l.discount_amount for l in computed_lines))
    taxable_total = _round(sum(l.taxable_amount for l in computed_lines))
    tax_total = _round(sum(l.tax_amount for l in computed_lines))

    coupon_discount = 0.0
    if coupon_discount_percent:
        coupon_discount = _round(taxable_total * (coupon_discount_percent / 100))
        if coupon_max_discount is not None:
            coupon_discount = min(coupon_discount, coupon_max_discount)

    total_discount = _round(line_discounts + coupon_discount)
    grand_total = _round(taxable_total + tax_total - coupon_discount)

    return BillCalculationResult(
        line_items=computed_lines,
        subtotal=subtotal,
        total_discount=total_discount,
        total_tax=tax_total,
        grand_total=grand_total,
        coupon_discount=coupon_discount,
    )
