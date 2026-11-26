from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services.employee_service import EmployeeService
from app.utils.decorators import admin_required

employee_bp = Blueprint("employees", __name__)
service = EmployeeService()


@employee_bp.route("/")
@login_required
@admin_required
def list_employees():
    return render_template("employees/list.html", employees=service.list_active())


@employee_bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_employee():
    if request.method == "POST":
        try:
            service.add_employee(
                name=request.form["name"].strip(),
                role=request.form["role"].strip(),
                phone=request.form["phone"].strip(),
                salary=float(request.form.get("salary") or 0),
                joining_date=datetime.strptime(request.form["joining_date"], "%Y-%m-%d").date(),
            )
            flash("Employee added.", "success")
            return redirect(url_for("employees.list_employees"))
        except (ValueError, KeyError) as exc:
            flash(str(exc), "danger")
    return render_template("employees/form.html", employee=None)


@employee_bp.route("/<int:employee_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_employee(employee_id):
    employee = service.repo.get_by_id(employee_id)
    if employee is None:
        flash("Employee not found.", "danger")
        return redirect(url_for("employees.list_employees"))

    if request.method == "POST":
        try:
            service.update_employee(
                employee_id,
                name=request.form["name"].strip(),
                role=request.form["role"].strip(),
                phone=request.form["phone"].strip(),
                salary=float(request.form.get("salary") or 0),
            )
            flash("Employee updated.", "success")
            return redirect(url_for("employees.list_employees"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("employees/form.html", employee=employee)


@employee_bp.route("/<int:employee_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_employee(employee_id):
    try:
        service.delete_employee(employee_id)
        flash("Employee deactivated.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("employees.list_employees"))


@employee_bp.route("/<int:employee_id>/attendance", methods=["POST"])
@login_required
@admin_required
def mark_attendance(employee_id):
    work_date = datetime.strptime(request.form["work_date"], "%Y-%m-%d").date()
    status = request.form.get("status", "present")
    service.mark_attendance(employee_id, work_date, status)
    flash("Attendance recorded.", "success")
    return redirect(url_for("employees.list_employees"))
