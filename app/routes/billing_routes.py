import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services.billing_service import BillingService, InsufficientStockError
from app.services.item_service import ItemService
from app.services.category_service import CategoryService
from app.repositories.bill_repository import BillRepository
from app.models.coupon import Coupon
from app.utils.qr_utils import bill_qr_data_uri

billing_bp = Blueprint("billing", __name__)
billing_service = BillingService()
item_service = ItemService()
category_service = CategoryService()
bill_repo = BillRepository()


@billing_bp.route("/")
@login_required
def pos():
    """The point-of-sale screen: item picker + live cart."""
    categories = category_service.list_all()
    available_items = item_service.search(status="available", per_page=500).items
    return render_template("billing/pos.html", categories=categories, items=available_items)


@billing_bp.route("/items.json")
@login_required
def items_json():
    """Lightweight JSON feed the POS page's JS uses for instant client-side search."""
    items = item_service.search(status="available", per_page=1000).items
    return jsonify([
        {
            "id": i.id, "name": i.name, "sku": i.sku,
            "price": float(i.price), "discount_percent": float(i.discount_percent),
            "tax_percent": float(i.tax_percent), "category_id": i.category_id,
            "available_qty": i.quantity_available,
        }
        for i in items
    ])


@billing_bp.route("/create", methods=["POST"])
@login_required
def create_bill():
    try:
        cart = json.loads(request.form.get("cart_json", "[]"))
        coupon_code = request.form.get("coupon_code", "").strip()
        coupon = None
        if coupon_code:
            coupon = Coupon.query.filter_by(code=coupon_code).first()
            if not coupon or not coupon.is_valid_today():
                flash("Coupon is invalid or expired.", "warning")
                coupon = None

        bill = billing_service.create_bill(
            cashier_id=current_user.id,
            cart=cart,
            customer_phone=request.form.get("customer_phone", "").strip() or None,
            customer_name=request.form.get("customer_name", "").strip() or None,
            coupon=coupon,
            payment_mode=request.form.get("payment_mode", "cash"),
        )
        flash(f"Bill {bill.bill_number} created successfully.", "success")
        return redirect(url_for("billing.receipt", bill_id=bill.id))
    except (ValueError, InsufficientStockError) as exc:
        flash(str(exc), "danger")
        return redirect(url_for("billing.pos"))


@billing_bp.route("/receipt/<int:bill_id>")
@login_required
def receipt(bill_id):
    bill = bill_repo.get_by_id(bill_id)
    if bill is None:
        flash("Bill not found.", "danger")
        return redirect(url_for("billing.pos"))
    qr_data_uri = bill_qr_data_uri(bill)
    return render_template("billing/receipt.html", bill=bill, qr_data_uri=qr_data_uri)


@billing_bp.route("/reprint")
@login_required
def reprint_lookup():
    bill_number = request.args.get("bill_number", "").strip()
    if not bill_number:
        return render_template("billing/reprint.html")
    bill = bill_repo.get_by_bill_number(bill_number)
    if not bill:
        flash("No bill found with that number.", "warning")
        return render_template("billing/reprint.html")
    return redirect(url_for("billing.receipt", bill_id=bill.id))
