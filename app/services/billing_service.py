from datetime import datetime
from app.extensions import db
from app.models.bill import Bill, BillItem
from app.models.item import Item
from app.repositories.bill_repository import BillRepository
from app.repositories.customer_repository import CustomerRepository
from app.services.billing_calculator import LineItemInput, calculate_bill


class InsufficientStockError(Exception):
    pass


class BillingService:
    def __init__(self):
        self.bill_repo = BillRepository()
        self.customer_repo = CustomerRepository()

    # ------------------------------------------------------------------
    def generate_bill_number(self) -> str:
        prefix = f"BILL-{datetime.utcnow().strftime('%Y%m%d')}-"
        latest = self.bill_repo.latest_bill_number_for_prefix(prefix)
        if latest:
            seq = int(latest.split("-")[-1]) + 1
        else:
            seq = 1
        return f"{prefix}{seq:04d}"

    # ------------------------------------------------------------------
    def create_bill(
        self,
        cashier_id,
        cart,  # list of {"item_id": int, "quantity": int}
        customer_phone=None,
        customer_name=None,
        coupon=None,
        payment_mode="cash",
    ) -> Bill:
        """
        Validate stock, run the pricing calculator, persist the Bill and
        its BillItems, decrement inventory, and accrue customer loyalty -
        all inside one atomic transaction.
        """
        if not cart:
            raise ValueError("Cannot create a bill with an empty cart.")

        items_by_id = {}
        line_inputs = []
        for row in cart:
            item = Item.query.get(row["item_id"])
            if item is None:
                raise ValueError(f"Item id {row['item_id']} does not exist.")
            quantity = int(row["quantity"])
            if not item.is_available:
                raise InsufficientStockError(f"'{item.name}' is currently unavailable.")
            if item.quantity_available < quantity:
                raise InsufficientStockError(
                    f"Only {item.quantity_available} left of '{item.name}'."
                )
            items_by_id[item.id] = item
            line_inputs.append(
                LineItemInput(
                    item_id=item.id,
                    name=item.name,
                    unit_price=float(item.price),
                    quantity=quantity,
                    discount_percent=float(item.discount_percent),
                    tax_percent=float(item.tax_percent),
                )
            )

        coupon_percent = float(coupon.discount_percent) if coupon else 0.0
        coupon_max = float(coupon.max_discount_amount) if (coupon and coupon.max_discount_amount) else None
        result = calculate_bill(line_inputs, coupon_percent, coupon_max)

        # Resolve / create customer (optional - walk-in customers allowed)
        customer = None
        if customer_phone:
            customer = self.customer_repo.get_by_phone(customer_phone)
            if customer is None and customer_name:
                from app.models.customer import Customer

                customer = Customer(name=customer_name, phone=customer_phone)
                db.session.add(customer)

        bill = Bill(
            bill_number=self.generate_bill_number(),
            cashier_id=cashier_id,
            customer_id=None,  # set after flush if customer created
            coupon_id=coupon.id if coupon else None,
            subtotal=result.subtotal,
            discount_amount=result.total_discount,
            tax_amount=result.total_tax,
            grand_total=result.grand_total,
            payment_mode=payment_mode,
        )
        db.session.add(bill)

        if customer:
            db.session.flush()  # ensure customer.id exists
            bill.customer_id = customer.id
            customer.add_purchase(result.grand_total)

        for line in result.line_items:
            db.session.add(
                BillItem(
                    bill=bill,
                    item_id=line.item_id,
                    item_name_snapshot=line.name,
                    unit_price=line.unit_price,
                    quantity=line.quantity,
                    discount_percent=line.discount_percent,
                    tax_percent=line.tax_percent,
                    line_total=line.line_total,
                )
            )
            # decrement stock
            items_by_id[line.item_id].quantity_available -= line.quantity

        if coupon:
            coupon.times_used = (coupon.times_used or 0) + 1

        db.session.commit()
        return bill

    def void_bill(self, bill: Bill):
        """Soft-cancel a bill (keeps it for audit trail instead of deleting)."""
        bill.status = "void"
        db.session.commit()
        return bill
