import enum
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models.mixins import TimestampMixin


class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    CASHIER = "cashier"


class User(db.Model, UserMixin, TimestampMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(RoleEnum), default=RoleEnum.CASHIER, nullable=False)
    is_active_flag = db.Column("is_active", db.Boolean, default=True, nullable=False)

    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=True)
    employee = db.relationship("Employee", back_populates="user_account", uselist=False)

    bills = db.relationship("Bill", back_populates="cashier", lazy="dynamic")

    # --- password helpers -------------------------------------------------
    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    # --- Flask-Login required property override ---------------------------
    @property
    def is_active(self):  # noqa: D401 - flask_login.UserMixin override
        return self.is_active_flag

    # --- role helpers -------------------------------------------------
    @property
    def is_admin(self) -> bool:
        return self.role == RoleEnum.ADMIN

    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"
