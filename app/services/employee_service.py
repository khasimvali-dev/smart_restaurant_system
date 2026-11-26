from app.repositories.employee_repository import EmployeeRepository


class EmployeeService:
    def __init__(self):
        self.repo = EmployeeRepository()

    def add_employee(self, **data):
        return self.repo.create(**data)

    def update_employee(self, employee_id, **data):
        employee = self.repo.get_by_id(employee_id)
        if employee is None:
            raise ValueError("Employee not found.")
        return self.repo.update(employee, **data)

    def delete_employee(self, employee_id):
        employee = self.repo.get_by_id(employee_id)
        if employee is None:
            raise ValueError("Employee not found.")
        # soft delete keeps payroll/attendance history intact
        self.repo.update(employee, is_active=False)

    def list_active(self):
        return self.repo.active_employees()

    def mark_attendance(self, employee_id, work_date, status, check_in=None, check_out=None):
        return self.repo.mark_attendance(employee_id, work_date, status, check_in, check_out)
