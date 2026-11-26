from app.models.employee import Employee, Attendance
from app.repositories.base_repository import BaseRepository


class EmployeeRepository(BaseRepository):
    model = Employee

    def active_employees(self):
        return Employee.query.filter_by(is_active=True).order_by(Employee.name.asc()).all()

    def mark_attendance(self, employee_id, work_date, status, check_in=None, check_out=None):
        record = Attendance.query.filter_by(
            employee_id=employee_id, work_date=work_date
        ).first()
        from app.extensions import db

        if record:
            record.status = status
            if check_in:
                record.check_in = check_in
            if check_out:
                record.check_out = check_out
        else:
            record = Attendance(
                employee_id=employee_id,
                work_date=work_date,
                status=status,
                check_in=check_in,
                check_out=check_out,
            )
            db.session.add(record)
        db.session.commit()
        return record
