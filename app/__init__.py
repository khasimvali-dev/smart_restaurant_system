import logging
import os
import shutil
from datetime import datetime
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template
from config import get_config
from app.extensions import db, login_manager, migrate, csrf


def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(get_config(config_name))

    _init_logging(app)
    _init_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_cli(app)
    _register_context_processors(app)

    with app.app_context():
        try:
            os.makedirs(app.config["EXPORT_DIR"], exist_ok=True)
        except OSError:
            pass
        try:
            os.makedirs(app.config["BACKUP_DIR"], exist_ok=True)
        except OSError:
            pass
        if app.config.get("AUTO_BACKUP_ON_STARTUP"):
            _auto_backup(app)
        _auto_seed(app)

    return app


def _init_logging(app):
    try:
        os.makedirs(app.config["LOG_DIR"], exist_ok=True)
        handler = RotatingFileHandler(
            os.path.join(app.config["LOG_DIR"], "app.log"), maxBytes=1_000_000, backupCount=5
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        app.logger.addHandler(handler)
    except OSError:
        # On read-only filesystems (e.g. Render free tier), fall back to stdout only
        logging.basicConfig(format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    app.logger.setLevel(app.config.get("LOG_LEVEL", "INFO"))


def _init_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


def _register_blueprints(app):
    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.item_routes import item_bp
    from app.routes.category_routes import category_bp
    from app.routes.billing_routes import billing_bp
    from app.routes.sales_routes import sales_bp
    from app.routes.analytics_routes import analytics_bp
    from app.routes.inventory_routes import inventory_bp
    from app.routes.employee_routes import employee_bp
    from app.routes.customer_routes import customer_bp
    from app.routes.report_routes import report_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(item_bp, url_prefix="/items")
    app.register_blueprint(category_bp, url_prefix="/categories")
    app.register_blueprint(billing_bp, url_prefix="/billing")
    app.register_blueprint(sales_bp, url_prefix="/sales")
    app.register_blueprint(analytics_bp, url_prefix="/analytics")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.register_blueprint(employee_bp, url_prefix="/employees")
    app.register_blueprint(customer_bp, url_prefix="/customers")
    app.register_blueprint(report_bp, url_prefix="/reports")


def _register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.exception("Unhandled server error")
        return render_template("errors/500.html"), 500


def _register_context_processors(app):
    @app.context_processor
    def inject_globals():
        return {
            "restaurant_name": app.config["RESTAURANT_NAME"],
            "currency_symbol": app.config["CURRENCY_SYMBOL"],
            "current_year": datetime.utcnow().year,
            "today_iso": datetime.utcnow().date().isoformat(),
        }


def _register_cli(app):
    @app.cli.command("seed-db")
    def seed_db():
        """Populate the database with demo categories/items/users. Usage: flask seed-db"""
        from database.seed import run_seed

        run_seed()
        print("Database seeded successfully.")

    @app.cli.command("backup-db")
    def backup_db_cmd():
        """Copy the current SQLite database file into the backups/ directory."""
        _auto_backup(app)
        print("Backup complete.")


def _auto_seed(app):
    """Seed the database with demo data on first run (when users table is empty)."""
    try:
        from app.models.user import User
        if User.query.count() == 0:
            app.logger.info("Empty database detected — running auto-seed.")
            from database.seed import run_seed
            run_seed()
            app.logger.info("Auto-seed complete.")
    except Exception as e:
        app.logger.warning("Auto-seed skipped: %s", e)


def _auto_backup(app):
    """Simple local file-copy backup - only meaningful for the SQLite fallback.
    For MySQL, use `mysqldump` on a schedule (see docs/ARCHITECTURE.md)."""
    db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    if not db_uri.startswith("sqlite"):
        app.logger.info("Auto-backup skipped: configured for MySQL (use mysqldump instead).")
        return
    db_path = db_uri.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        return
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(app.config["BACKUP_DIR"], f"smart_restaurant_{timestamp}.db")
    shutil.copy2(db_path, dest)
    app.logger.info("Database backed up to %s", dest)
