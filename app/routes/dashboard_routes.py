from datetime import datetime, timedelta
from flask import Blueprint, render_template
from flask_login import login_required
from app.repositories.bill_repository import BillRepository
from app.repositories.item_repository import ItemRepository
from app.services.analytics_service import AnalyticsService

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    bill_repo = BillRepository()
    item_repo = ItemRepository()
    analytics = AnalyticsService()

    today = datetime.utcnow().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    today_stats = bill_repo.today_stats()

    week_bills = bill_repo.bills_between(
        datetime.combine(week_start, datetime.min.time()), datetime.utcnow()
    )
    month_bills = bill_repo.bills_between(
        datetime.combine(month_start, datetime.min.time()), datetime.utcnow()
    )

    recent_bills = bill_repo.search(page=1, per_page=8).items
    top_items, _ = analytics.top_items(limit=5)
    low_stock = item_repo.low_stock_items(threshold=10)

    kpis = {
        "today_sales": today_stats["total_sales"],
        "today_orders": today_stats["count"],
        "week_sales": sum(float(b.grand_total) for b in week_bills),
        "month_sales": sum(float(b.grand_total) for b in month_bills),
        "month_orders": len(month_bills),
        "total_revenue_all_time": sum(float(b.grand_total) for b in bill_repo.get_all()),
    }

    return render_template(
        "dashboard/index.html",
        kpis=kpis,
        recent_bills=recent_bills,
        top_items=top_items,
        low_stock=low_stock,
    )
