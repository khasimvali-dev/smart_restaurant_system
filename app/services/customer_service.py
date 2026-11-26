from app.repositories.customer_repository import CustomerRepository
from app.repositories.bill_repository import BillRepository


class CustomerService:
    def __init__(self):
        self.repo = CustomerRepository()
        self.bill_repo = BillRepository()

    def add_customer(self, **data):
        if self.repo.get_by_phone(data.get("phone")):
            raise ValueError("A customer with this phone number already exists.")
        return self.repo.create(**data)

    def update_customer(self, customer_id, **data):
        customer = self.repo.get_by_id(customer_id)
        if customer is None:
            raise ValueError("Customer not found.")
        return self.repo.update(customer, **data)

    def search(self, keyword=None, page=1, per_page=20):
        return self.repo.search(keyword=keyword, page=page, per_page=per_page)

    def history(self, customer_id):
        customer = self.repo.get_by_id(customer_id)
        if customer is None:
            raise ValueError("Customer not found.")
        return customer.bills.order_by(self.bill_repo.model.bill_date.desc()).all()
