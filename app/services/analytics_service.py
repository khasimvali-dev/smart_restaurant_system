"""
Analytics service: turns raw Bill / BillItem rows into pandas DataFrames,
then produces Plotly figures rendered to HTML <div> snippets that the
templates embed directly (no extra JS files, no external image hosting -
fully local, as the brief requires).
"""
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.io as pio
from app.models.bill import Bill, BillItem

pio.templates.default = "plotly_white"


def _bills_dataframe(start_date=None, end_date=None):
    query = Bill.query.filter(Bill.status == "completed")
    if start_date:
        query = query.filter(Bill.bill_date >= start_date)
    if end_date:
        query = query.filter(Bill.bill_date < end_date + timedelta(days=1))
    rows = [
        {
            "bill_id": b.id,
            "bill_number": b.bill_number,
            "date": b.bill_date.date(),
            "hour": b.bill_date.hour,
            "month": b.bill_date.strftime("%Y-%m"),
            "year": b.bill_date.year,
            "customer_id": b.customer_id,
            "grand_total": float(b.grand_total),
        }
        for b in query.all()
    ]
    return pd.DataFrame(rows)


def _bill_items_dataframe(start_date=None, end_date=None):
    query = BillItem.query.join(Bill).filter(Bill.status == "completed")
    if start_date:
        query = query.filter(Bill.bill_date >= start_date)
    if end_date:
        query = query.filter(Bill.bill_date < end_date + timedelta(days=1))
    rows = [
        {
            "bill_id": bi.bill_id,
            "item_id": bi.item_id,
            "item_name": bi.item_name_snapshot,
            "category": bi.item.category.name if bi.item and bi.item.category else "Unknown",
            "quantity": bi.quantity,
            "line_total": float(bi.line_total),
            "date": bi.bill.bill_date.date(),
        }
        for bi in query.all()
    ]
    return pd.DataFrame(rows)


class AnalyticsService:
    """All methods return (dataframe_summary: dict, chart_html: str) tuples
    so routes/templates can show both numeric KPIs and a visualization."""

    # ---------------------- Sales trend analysis -----------------------
    def sales_trend(self, granularity="daily", start_date=None, end_date=None):
        df = _bills_dataframe(start_date, end_date)
        if df.empty:
            return {"total": 0, "average": 0}, "<p class='text-muted'>No sales data yet.</p>"

        if granularity == "daily":
            grouped = df.groupby("date")["grand_total"].sum().reset_index()
            x_col = "date"
        elif granularity == "weekly":
            df["week"] = pd.to_datetime(df["date"]).dt.to_period("W").apply(lambda p: p.start_time.date())
            grouped = df.groupby("week")["grand_total"].sum().reset_index()
            x_col = "week"
        elif granularity == "monthly":
            grouped = df.groupby("month")["grand_total"].sum().reset_index()
            x_col = "month"
        else:  # yearly
            grouped = df.groupby("year")["grand_total"].sum().reset_index()
            x_col = "year"

        fig = px.line(
            grouped, x=x_col, y="grand_total", markers=True,
            labels={"grand_total": "Revenue", x_col: granularity.capitalize()},
            title=f"{granularity.capitalize()} Sales Trend",
        )
        fig.update_layout(height=380, margin=dict(l=20, r=20, t=50, b=20))
        summary = {
            "total": round(df["grand_total"].sum(), 2),
            "average": round(df["grand_total"].mean(), 2),
            "count": len(df),
        }
        return summary, pio.to_html(fig, full_html=False, include_plotlyjs=False)

    # ---------------------- Product analysis -----------------------
    def top_items(self, limit=10, start_date=None, end_date=None):
        df = _bill_items_dataframe(start_date, end_date)
        if df.empty:
            return [], "<p class='text-muted'>No item sales yet.</p>"
        grouped = (
            df.groupby("item_name")
            .agg(units_sold=("quantity", "sum"), revenue=("line_total", "sum"))
            .reset_index()
            .sort_values("units_sold", ascending=False)
            .head(limit)
        )
        fig = px.bar(
            grouped, x="item_name", y="units_sold", color="revenue",
            labels={"item_name": "Item", "units_sold": "Units Sold"},
            title="Top Selling Items",
        )
        fig.update_layout(height=380, margin=dict(l=20, r=20, t=50, b=20))
        return grouped.to_dict("records"), pio.to_html(fig, full_html=False, include_plotlyjs=False)

    def least_sold_items(self, limit=10, start_date=None, end_date=None):
        df = _bill_items_dataframe(start_date, end_date)
        if df.empty:
            return []
        grouped = (
            df.groupby("item_name")
            .agg(units_sold=("quantity", "sum"))
            .reset_index()
            .sort_values("units_sold", ascending=True)
            .head(limit)
        )
        return grouped.to_dict("records")

    def revenue_by_category(self, start_date=None, end_date=None):
        df = _bill_items_dataframe(start_date, end_date)
        if df.empty:
            return "<p class='text-muted'>No category data yet.</p>"
        grouped = df.groupby("category")["line_total"].sum().reset_index()
        fig = px.pie(
            grouped, names="category", values="line_total",
            title="Revenue Share by Category", hole=0.45,
        )
        fig.update_layout(height=380, margin=dict(l=20, r=20, t=50, b=20))
        return pio.to_html(fig, full_html=False, include_plotlyjs=False)

    # ---------------------- Customer analysis -----------------------
    def peak_hours_heatmap(self, start_date=None, end_date=None):
        df = _bills_dataframe(start_date, end_date)
        if df.empty:
            return "<p class='text-muted'>No order-time data yet.</p>"
        df["weekday"] = pd.to_datetime(df["date"]).dt.day_name()
        pivot = df.pivot_table(
            index="weekday", columns="hour", values="grand_total",
            aggfunc="count", fill_value=0,
        )
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        pivot = pivot.reindex([d for d in weekday_order if d in pivot.index])
        fig = px.imshow(
            pivot, labels=dict(x="Hour of Day", y="Day", color="Orders"),
            title="Peak Ordering Hours", aspect="auto", color_continuous_scale="Oranges",
        )
        fig.update_layout(height=380, margin=dict(l=20, r=20, t=50, b=20))
        return pio.to_html(fig, full_html=False, include_plotlyjs=False)

    def average_bill_value(self, start_date=None, end_date=None):
        df = _bills_dataframe(start_date, end_date)
        if df.empty:
            return 0.0
        return round(df["grand_total"].mean(), 2)

    def frequent_customers(self, limit=10):
        from app.repositories.customer_repository import CustomerRepository

        return CustomerRepository().top_customers(limit)
