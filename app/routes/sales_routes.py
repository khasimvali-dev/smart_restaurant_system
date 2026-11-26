from datetime import datetime
from flask import Blueprint, render_template, request
from flask_login import login_required
from app.repositories.bill_repository import BillRepository

sales_bp = Blueprint("sales", __name__)
bill_repo = BillRepository()


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


@sales_bp.route("/")
@login_required
def history():
    page = request.args.get("page", 1, type=int)
    date_from = _parse_date(request.args.get("date_from"))
    date_to = _parse_date(request.args.get("date_to"))
    bill_number = request.args.get("bill_number")

    pagination = bill_repo.search(
        date_from=date_from, date_to=date_to, bill_number=bill_number, page=page, per_page=20
    )
    filters = {k: v for k, v in request.args.items() if k != "page"}
    return render_template("sales/history.html", pagination=pagination, bills=pagination.items, filters=filters)
