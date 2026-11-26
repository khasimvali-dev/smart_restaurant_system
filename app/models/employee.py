from datetime import date
from app.extensions import db
from app.models.mixins import TimestampMixin, SoftDeleteMixin


class Employee(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(60), nullable=False)  # e.g. Chef, Waiter, Manager
    phone = db.Column(db.String(20), nullable=False)
    salary = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    joining_date = db.Column(db.Date, nullable=False, default=date.today)

    user_account = db.relationship("User", back_populates="employee", uselist=False)
    attendance_records = db.relationship(
        "Attendance", back_populates="employee", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Employee {self.name} - {self.role}>"


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    work_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), nullable=False, default="present")  # present/absent/leave
    check_in = db.Column(db.Time, nullable=True)
    check_out = db.Column(db.Time, nullable=True)

    employee = db.relationship("Employee", back_populates="attendance_records")

    __table_args__ = (
        db.UniqueConstraint("employee_id", "work_date", name="uq_employee_date"),
    )
