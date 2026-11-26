from app.extensions import db
from app.models.mixins import TimestampMixin


class InventoryItem(db.Model, TimestampMixin):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    unit = db.Column(db.String(20), nullable=False, default="kg")  # kg, litre, pcs, ...
    minimum_stock = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    @property
    def stock_status(self) -> str:
        if self.quantity <= 0:
            return "out_of_stock"
        if self.quantity <= self.minimum_stock:
            return "low_stock"
        return "ok"

    def __repr__(self):
        return f"<InventoryItem {self.name}: {self.quantity}{self.unit}>"
