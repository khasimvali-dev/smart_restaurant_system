from datetime import datetime
from app.extensions import db
from app.models.mixins import TimestampMixin


class Bill(db.Model, TimestampMixin):
    __tablename__ = "bills"

    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    bill_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    cashier_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey("coupons.id"), nullable=True)

    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    discount_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    tax_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    grand_total = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    payment_mode = db.Column(db.String(20), default="cash", nullable=False)  # cash/card/upi
    status = db.Column(db.String(20), default="completed", nullable=False)  # completed/void

    cashier = db.relationship("User", back_populates="bills")
    customer = db.relationship("Customer", back_populates="bills")
    coupon = db.relationship("Coupon")
    line_items = db.relationship(
        "BillItem", back_populates="bill", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Bill {self.bill_number} - {self.grand_total}>"


class BillItem(db.Model):
    __tablename__ = "bill_items"

    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey("bills.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)

    item_name_snapshot = db.Column(db.String(120), nullable=False)  # preserved even if item edited later
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    discount_percent = db.Column(db.Numeric(5, 2), default=0, nullable=False)
    tax_percent = db.Column(db.Numeric(5, 2), default=0, nullable=False)
    line_total = db.Column(db.Numeric(12, 2), nullable=False)

    bill = db.relationship("Bill", back_populates="line_items")
    item = db.relationship("Item", back_populates="bill_items")
