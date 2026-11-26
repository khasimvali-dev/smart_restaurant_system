from app.models.customer import Customer
from app.repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository):
    model = Customer

    def get_by_phone(self, phone):
        return Customer.query.filter_by(phone=phone).first()

    def search(self, keyword=None, page=1, per_page=20):
        query = Customer.query
        if keyword:
            like = f"%{keyword}%"
            query = query.filter(
                (Customer.name.ilike(like)) | (Customer.phone.ilike(like))
            )
        query = query.order_by(Customer.name.asc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def top_customers(self, limit=10):
        return Customer.query.order_by(Customer.total_spend.desc()).limit(limit).all()
