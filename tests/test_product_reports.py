def test_product_report_page_and_qr(client):
    detail = client.get("/shop/vanilla")
    assert detail.status_code == 200
    assert b"Product lab report" in detail.data
    assert b"/reports/vanilla" in detail.data
    assert b"/reports/qr/vanilla.png" in detail.data

    report = client.get("/reports/vanilla")
    assert report.status_code == 200
    assert b"Vanilla" in report.data
    assert b"Results not yet published" in report.data
    assert b"0.38" not in report.data

    qr = client.get("/reports/qr/vanilla.png")
    assert qr.status_code == 200
    assert qr.mimetype == "image/png"


def test_reports_are_available_for_each_active_product(client, app):
    from app.extensions import db
    from app.models import Flavor, Product

    with app.app_context():
        flavor = Flavor.query.filter_by(slug="chocolate").first()
        if flavor is None:
            flavor = Flavor(name="Chocolate", slug="chocolate")
            db.session.add(flavor)
            db.session.flush()
        product = Product(
            name="Dark Chocolate",
            slug="dark-chocolate",
            sku="DCH-001",
            flavor=flavor,
            is_active=True,
        )
        db.session.add(product)
        db.session.commit()

    assert client.get("/reports/dark-chocolate").status_code == 200
    assert client.get("/reports/qr/dark-chocolate.png").status_code == 200
    assert client.get("/reports/unknown-product").status_code == 404
    assert client.get("/verify/van-001").status_code == 404

def test_qr_uses_public_base_url_not_request_host(app):
    """QR codes must never encode a local address like 127.0.0.1."""
    from app.routes.reports import public_report_url

    app.config["PUBLIC_BASE_URL"] = "https://absolute-icecream.onrender.com"
    with app.test_request_context("/", base_url="http://127.0.0.1:5000"):
        assert public_report_url("vanilla") == (
            "https://absolute-icecream.onrender.com/reports/vanilla"
        )
    page = app.test_client().get("/reports/vanilla", base_url="http://127.0.0.1:5000")
    assert b"https://absolute-icecream.onrender.com/reports/vanilla" in page.data
    assert b"127.0.0.1" not in page.data


def test_proxy_headers_give_https_address(monkeypatch):
    """Behind a hosting proxy, fall back to the forwarded https host."""
    monkeypatch.setenv("TEST_DATABASE_URL", "sqlite://")
    monkeypatch.delenv("PUBLIC_BASE_URL", raising=False)
    monkeypatch.delenv("RENDER_EXTERNAL_URL", raising=False)
    from app import create_app
    from app.routes.reports import public_report_url

    app = create_app("testing")
    app.config["PUBLIC_BASE_URL"] = ""
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    captured = {}

    @app.get("/_probe")
    def _probe():
        captured["url"] = public_report_url("vanilla")
        return "ok"

    app.test_client().get(
        "/_probe",
        base_url="http://10.0.0.5:8000",
        headers={"X-Forwarded-Proto": "https", "X-Forwarded-Host": "shop.example.com"},
    )
    assert captured["url"] == "https://shop.example.com/reports/vanilla"


def test_sample_lab_report_only_when_enabled(app):
    from app.extensions import db
    from app.models import Flavor, Product

    with app.app_context():
        flavor = Flavor(name="Chocolate", slug="chocolate")
        db.session.add(Product(name="Dark Chocolate", slug="dark-chocolate",
                               sku="DCH-002", flavor=flavor, is_active=True))
        db.session.commit()

    client = app.test_client()
    app.config["SHOW_SAMPLE_LAB_REPORTS"] = False
    off = client.get("/reports/dark-chocolate")
    assert b"Results not yet published" in off.data and b"0.38" not in off.data

    app.config["SHOW_SAMPLE_LAB_REPORTS"] = True
    on = client.get("/reports/dark-chocolate")
    assert b"Sample report" in on.data
    assert b"0.38" in on.data
    assert b"Within the 0.5 g sugar-free limit" in on.data
