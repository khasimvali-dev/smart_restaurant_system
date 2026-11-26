from datetime import datetime
from app.extensions import db


class TimestampMixin:
    """Adds created_at / updated_at to any model that inherits it."""

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class SoftDeleteMixin:
    """Adds a soft-delete flag so records can be hidden without losing history."""

    is_active = db.Column(db.Boolean, default=True, nullable=False)
