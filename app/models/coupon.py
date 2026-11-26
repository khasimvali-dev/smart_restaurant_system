from datetime import date
from app.extensions import db
from app.models.mixins import TimestampMixin


class Coupon(db.Model, TimestampMixin):
    __tablename__ = "coupons"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    discount_percent = db.Column(db.Numeric(5, 2), nullable=False)
    max_discount_amount = db.Column(db.Numeric(10, 2), nullable=True)
    valid_from = db.Column(db.Date, nullable=False, default=date.today)
    valid_until = db.Column(db.Date, nullable=False)
    usage_limit = db.Column(db.Integer, nullable=True)  # None = unlimited
    times_used = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def is_valid_today(self) -> bool:
        today = date.today()
        if not self.is_active:
            return False
        if not (self.valid_from <= today <= self.valid_until):
            return False
        if self.usage_limit is not None and self.times_used >= self.usage_limit:
            return False
        return True

    def __repr__(self):
        return f"<Coupon {self.code}>"
