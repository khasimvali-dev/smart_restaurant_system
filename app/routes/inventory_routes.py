from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services.inventory_service import InventoryService
from app.utils.decorators import admin_required

inventory_bp = Blueprint("inventory", __name__)
service = InventoryService()


@inventory_bp.route("/")
@login_required
def list_inventory():
    return render_template(
        "inventory/list.html",
        items=service.all_items(),
        alerts=service.low_stock_alerts(),
    )


@inventory_bp.route("/add", methods=["POST"])
@login_required
@admin_required
def add_inventory():
    try:
        service.add_inventory(
            name=request.form["name"].strip(),
            quantity=float(request.form["quantity"]),
            unit=request.form.get("unit", "kg"),
            minimum_stock=float(request.form.get("minimum_stock") or 0),
        )
        flash("Ingredient added to inventory.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("inventory.list_inventory"))


@inventory_bp.route("/<int:inventory_id>/update", methods=["POST"])
@login_required
@admin_required
def update_inventory(inventory_id):
    try:
        service.update_inventory(
            inventory_id,
            quantity=float(request.form["quantity"]),
            unit=request.form.get("unit", "kg"),
            minimum_stock=float(request.form.get("minimum_stock") or 0),
        )
        flash("Inventory updated.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("inventory.list_inventory"))


@inventory_bp.route("/<int:inventory_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_inventory(inventory_id):
    try:
        service.remove_inventory(inventory_id)
        flash("Ingredient removed.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("inventory.list_inventory"))
