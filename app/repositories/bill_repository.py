from datetime import datetime, timedelta
from app.models.bill import Bill
from app.repositories.base_repository import BaseRepository


class BillRepository(BaseRepository):
    model = Bill

    def get_by_bill_number(self, bill_number):
        return Bill.query.filter_by(bill_number=bill_number).first()

    def latest_bill_number_for_prefix(self, prefix):
        row = (
            Bill.query.filter(Bill.bill_number.like(f"{prefix}%"))
            .order_by(Bill.id.desc())
            .first()
        )
        return row.bill_number if row else None

    def search(self, date_from=None, date_to=None, bill_number=None, customer_id=None,
               page=1, per_page=20):
        query = Bill.query
        if date_from:
            query = query.filter(Bill.bill_date >= date_from)
        if date_to:
            # include the whole end day
            query = query.filter(Bill.bill_date < date_to + timedelta(days=1))
        if bill_number:
            query = query.filter(Bill.bill_number.ilike(f"%{bill_number}%"))
        if customer_id:
            query = query.filter(Bill.customer_id == customer_id)
        query = query.order_by(Bill.bill_date.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def bills_between(self, start_dt, end_dt):
        return (
            Bill.query.filter(Bill.bill_date >= start_dt, Bill.bill_date <= end_dt)
            .order_by(Bill.bill_date.asc())
            .all()
        )

    def today_stats(self):
        today = datetime.utcnow().date()
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())
        bills = self.bills_between(start, end)
        total_sales = sum(float(b.grand_total) for b in bills)
        return {"count": len(bills), "total_sales": total_sales}
