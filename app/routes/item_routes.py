from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required
from app.services.item_service import ItemService
from app.services.category_service import CategoryService
from app.utils.decorators import admin_required

item_bp = Blueprint("items", __name__)
service = ItemService()
category_service = CategoryService()


@item_bp.route("/")
@login_required
def list_items():
    page = request.args.get("page", 1, type=int)
    keyword = request.args.get("q")
    category_id = request.args.get("category_id", type=int)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    status = request.args.get("status")

    pagination = service.search(
        keyword=keyword, category_id=category_id, min_price=min_price,
        max_price=max_price, status=status, page=page, per_page=15,
    )
    return render_template(
        "items/list.html",
        pagination=pagination,
        items=pagination.items,
        categories=category_service.list_all(),
        filters={k: v for k, v in request.args.items() if k != "page"},
    )


@item_bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_item():
    if request.method == "POST":
        try:
            service.create_item(
                sku=request.form["sku"].strip(),
                name=request.form["name"].strip(),
                category_id=int(request.form["category_id"]),
                price=float(request.form["price"]),
                discount_percent=float(request.form.get("discount_percent") or 0),
                tax_percent=float(request.form.get("tax_percent") or 5.0),
                quantity_available=int(request.form.get("quantity_available") or 0),
                status=request.form.get("status", "available"),
            )
            flash("Item added successfully.", "success")
            return redirect(url_for("items.list_items"))
        except (ValueError, KeyError) as exc:
            flash(str(exc), "danger")
    return render_template("items/form.html", item=None, categories=category_service.list_all())


@item_bp.route("/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_item(item_id):
    item = service.repo.get_by_id(item_id)
    if item is None:
        flash("Item not found.", "danger")
        return redirect(url_for("items.list_items"))

    if request.method == "POST":
        try:
            service.update_item(
                item_id,
                name=request.form["name"].strip(),
                category_id=int(request.form["category_id"]),
                price=float(request.form["price"]),
                discount_percent=float(request.form.get("discount_percent") or 0),
                tax_percent=float(request.form.get("tax_percent") or 5.0),
                quantity_available=int(request.form.get("quantity_available") or 0),
                status=request.form.get("status", "available"),
            )
            flash("Item updated.", "success")
            return redirect(url_for("items.list_items"))
        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template("items/form.html", item=item, categories=category_service.list_all())


@item_bp.route("/<int:item_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_item(item_id):
    try:
        service.delete_item(item_id)
        flash("Item deleted.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("items.list_items"))


@item_bp.route("/bulk-update-prices", methods=["POST"])
@login_required
@admin_required
def bulk_update_prices():
    item_ids = request.form.getlist("item_ids", type=int)
    percent_change = request.form.get("percent_change", type=float)
    if not item_ids or percent_change is None:
        flash("Select at least one item and a percentage change.", "warning")
    else:
        service.bulk_update_prices(item_ids, percent_change)
        flash(f"Updated prices for {len(item_ids)} item(s).", "success")
    return redirect(url_for("items.list_items"))


@item_bp.route("/export")
@login_required
@admin_required
def export_items():
    csv_data = service.export_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=items_export.csv"},
    )
