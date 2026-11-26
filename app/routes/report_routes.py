from datetime import datetime, date
from flask import Blueprint, render_template, request, Response, current_app
from flask_login import login_required
from app.services.report_service import ReportService
from app.utils.decorators import admin_required

report_bp = Blueprint("reports", __name__)
service = ReportService()


def _parse_date(value, default):
    if not value:
        return default
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return default


@report_bp.route("/")
@login_required
@admin_required
def index():
    return render_template("reports/index.html", today=date.today().isoformat())


@report_bp.route("/sales/csv")
@login_required
@admin_required
def sales_csv():
    date_from = _parse_date(request.args.get("date_from"), date.today())
    date_to = _parse_date(request.args.get("date_to"), date.today())
    start_dt = datetime.combine(date_from, datetime.min.time())
    end_dt = datetime.combine(date_to, datetime.max.time())
    data = service.sales_csv(start_dt, end_dt)
    return Response(
        data, mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=sales_{date_from}_{date_to}.csv"},
    )


@report_bp.route("/sales/excel")
@login_required
@admin_required
def sales_excel():
    date_from = _parse_date(request.args.get("date_from"), date.today())
    date_to = _parse_date(request.args.get("date_to"), date.today())
    start_dt = datetime.combine(date_from, datetime.min.time())
    end_dt = datetime.combine(date_to, datetime.max.time())
    data = service.sales_excel_bytes(start_dt, end_dt)
    return Response(
        data,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=sales_{date_from}_{date_to}.xlsx"},
    )


@report_bp.route("/sales/daily-pdf")
@login_required
@admin_required
def daily_sales_pdf():
    report_date = _parse_date(request.args.get("date"), date.today())
    data = service.daily_sales_pdf_bytes(report_date, current_app.config["RESTAURANT_NAME"])
    return Response(
        data, mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=daily_sales_{report_date}.pdf"},
    )


@report_bp.route("/tax-report/pdf")
@login_required
@admin_required
def tax_report_pdf():
    date_from = _parse_date(request.args.get("date_from"), date.today())
    date_to = _parse_date(request.args.get("date_to"), date.today())
    data = service.tax_report_pdf_bytes(
        date_from, date_to, current_app.config["RESTAURANT_NAME"], current_app.config["RESTAURANT_GSTIN"]
    )
    return Response(
        data, mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=tax_report_{date_from}_{date_to}.pdf"},
    )


@report_bp.route("/inventory/csv")
@login_required
@admin_required
def inventory_csv():
    data = service.inventory_csv()
    return Response(
        data, mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventory_report.csv"},
    )


@report_bp.route("/employees/csv")
@login_required
@admin_required
def employees_csv():
    data = service.employee_csv()
    return Response(
        data, mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=employee_report.csv"},
    )
