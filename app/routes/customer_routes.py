from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services.customer_service import CustomerService

customer_bp = Blueprint("customers", __name__)
service = CustomerService()


@customer_bp.route("/")
@login_required
def list_customers():
    page = request.args.get("page", 1, type=int)
    keyword = request.args.get("q")
    pagination = service.search(keyword=keyword, page=page, per_page=20)
    filters = {k: v for k, v in request.args.items() if k != "page"}
    return render_template("customers/list.html", pagination=pagination, customers=pagination.items, filters=filters)


@customer_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_customer():
    if request.method == "POST":
        try:
            service.add_customer(
                name=request.form["name"].strip(),
                phone=request.form["phone"].strip(),
                email=request.form.get("email", "").strip() or None,
            )
            flash("Customer added.", "success")
            return redirect(url_for("customers.list_customers"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("customers/form.html", customer=None)


@customer_bp.route("/<int:customer_id>")
@login_required
def customer_detail(customer_id):
    customer = service.repo.get_by_id(customer_id)
    if customer is None:
        flash("Customer not found.", "danger")
        return redirect(url_for("customers.list_customers"))
    bills = service.history(customer_id)
    return render_template("customers/detail.html", customer=customer, bills=bills)
