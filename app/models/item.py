from app.extensions import db
from app.models.mixins import TimestampMixin


class Item(db.Model, TimestampMixin):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(30), unique=True, nullable=False, index=True)  # human item code
    name = db.Column(db.String(120), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_percent = db.Column(db.Numeric(5, 2), default=0, nullable=False)
    tax_percent = db.Column(db.Numeric(5, 2), default=5.0, nullable=False)
    quantity_available = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.String(15), default="available", nullable=False)  # available/unavailable
    image_filename = db.Column(db.String(255), nullable=True)

    category = db.relationship("Category", back_populates="items")
    bill_items = db.relationship("BillItem", back_populates="item")

    @property
    def is_available(self) -> bool:
        return self.status == "available" and self.quantity_available > 0

    @property
    def net_price(self):
        """Price after per-item discount, before tax."""
        discount = (self.price * self.discount_percent) / 100
        return round(float(self.price) - float(discount), 2)

    def __repr__(self):
        return f"<Item {self.sku} - {self.name}>"
