from datetime import datetime
from flask import Blueprint, render_template, request
from flask_login import login_required
from app.utils.decorators import admin_required
from app.services.analytics_service import AnalyticsService

analytics_bp = Blueprint("analytics", __name__)
service = AnalyticsService()


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


@analytics_bp.route("/")
@login_required
@admin_required
def index():
    granularity = request.args.get("granularity", "daily")
    date_from = _parse_date(request.args.get("date_from"))
    date_to = _parse_date(request.args.get("date_to"))

    trend_summary, trend_chart = service.sales_trend(granularity, date_from, date_to)
    top_items, top_items_chart = service.top_items(limit=10, start_date=date_from, end_date=date_to)
    least_items = service.least_sold_items(limit=5, start_date=date_from, end_date=date_to)
    category_chart = service.revenue_by_category(date_from, date_to)
    heatmap_chart = service.peak_hours_heatmap(date_from, date_to)
    avg_bill = service.average_bill_value(date_from, date_to)
    frequent_customers = service.frequent_customers(limit=8)

    return render_template(
        "analytics/index.html",
        granularity=granularity,
        trend_summary=trend_summary,
        trend_chart=trend_chart,
        top_items=top_items,
        top_items_chart=top_items_chart,
        least_items=least_items,
        category_chart=category_chart,
        heatmap_chart=heatmap_chart,
        avg_bill=avg_bill,
        frequent_customers=frequent_customers,
        filters=request.args,
    )
