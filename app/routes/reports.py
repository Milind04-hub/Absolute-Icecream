from flask import Blueprint, abort, current_app, render_template, send_file, url_for

from app.data.lab_reports import get_sample_report
from app.models.product import Product
from app.services.qr_service import generate_qr_code


reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


def _public_product(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first()
    if product is None:
        abort(404)
    return product


def public_report_url(slug):
    """Address a phone should open for this product's report.

    Uses PUBLIC_BASE_URL when set, so QR codes never encode a local or
    internal address such as http://127.0.0.1:5000.
    """
    path = url_for("reports.product_report", slug=slug)
    base = current_app.config.get("PUBLIC_BASE_URL")
    if base:
        return f"{base}{path}"
    return url_for("reports.product_report", slug=slug, _external=True)


@reports_bp.get("/<slug>")
def product_report(slug):
    """Show the product-specific laboratory report and available facts."""
    product = _public_product(slug)
    lab = None
    if current_app.config.get("SHOW_SAMPLE_LAB_REPORTS"):
        lab = get_sample_report(slug)
    return render_template(
        "product_report.html",
        product=product,
        lab=lab,
        report_url=public_report_url(slug),
    )


@reports_bp.get("/qr/<slug>.png")
def product_report_qr(slug):
    """Generate a QR code that opens this product's report page."""
    _public_product(slug)
    output = generate_qr_code(public_report_url(slug))
    return send_file(output, mimetype="image/png", download_name=f"{slug}-report.png")
