"""Prepare the database on start-up for free hosting.

Runs migrations, then seeds the product catalogue if it is empty. Safe to run
on every boot. On hosts with a temporary disk (such as Render's free tier with
SQLite), the database is rebuilt on each restart, which is fine for a demo.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_migrate import upgrade  # noqa: E402

from app import create_app  # noqa: E402
from app.models.product import Product  # noqa: E402


def main():
    app = create_app(os.getenv("FLASK_CONFIG", "production"))
    with app.app_context():
        upgrade()
        if Product.query.count() == 0:
            from app.seed.seed_products import seed_products
            seed_products()
        if os.getenv("ADMIN_EMAIL") and os.getenv("ADMIN_PASSWORD"):
            from app.seed.admin import create_initial_admin
            create_initial_admin()
        base = app.config.get("PUBLIC_BASE_URL")
        print(f"Bootstrap complete. QR codes will point to: {base or '(request host)'}")


if __name__ == "__main__":
    main()
