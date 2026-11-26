from app.extensions import db
from app.models.mixins import TimestampMixin


class Category(db.Model, TimestampMixin):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    items = db.relationship("Item", back_populates="category", lazy="dynamic")

    def __repr__(self):
        return f"<Category {self.name}>"
