from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services.category_service import CategoryService
from app.utils.decorators import admin_required

category_bp = Blueprint("categories", __name__)
service = CategoryService()


@category_bp.route("/")
@login_required
def list_categories():
    return render_template("categories/list.html", categories=service.list_all())


@category_bp.route("/add", methods=["POST"])
@login_required
@admin_required
def add_category():
    try:
        service.create_category(
            name=request.form["name"].strip(),
            description=request.form.get("description", "").strip(),
        )
        flash("Category added.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("categories.list_categories"))


@category_bp.route("/<int:category_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_category(category_id):
    try:
        service.update_category(
            category_id,
            name=request.form["name"].strip(),
            description=request.form.get("description", "").strip(),
        )
        flash("Category updated.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("categories.list_categories"))


@category_bp.route("/<int:category_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_category(category_id):
    try:
        service.delete_category(category_id)
        flash("Category deleted.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("categories.list_categories"))
