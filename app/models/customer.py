from app.extensions import db
from app.models.mixins import TimestampMixin


class Customer(db.Model, TimestampMixin):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), nullable=True)
    loyalty_points = db.Column(db.Integer, default=0, nullable=False)
    total_spend = db.Column(db.Numeric(12, 2), default=0, nullable=False)

    bills = db.relationship("Bill", back_populates="customer", lazy="dynamic")

    def add_purchase(self, bill_total, points_per_100=1):
        """Update aggregate spend and accrue loyalty points (1 pt / Rs.100 by default)."""
        self.total_spend = (self.total_spend or 0) + bill_total
        self.loyalty_points = (self.loyalty_points or 0) + int(bill_total // 100) * points_per_100

    def __repr__(self):
        return f"<Customer {self.name} ({self.phone})>"
