"""Sample laboratory results for the demo deployment.

These values are illustrative only. They are shown solely when the
SHOW_SAMPLE_LAB_REPORTS setting is enabled, and the report page labels them
as a sample. Replace them with verified results from an accredited lab
before any public launch.
"""

SUGAR_LIMIT_G = 0.5  # FSSAI "sugar free": not more than 0.5 g per 100 g

_SWEETENERS = [
    ("Erythritol", "9.8 g", "sugar alcohol, not counted as sugar"),
    ("Steviol glycosides", "present", "from stevia"),
    ("Maltitol", None, None),
    ("Sucralose", None, None),
]

SAMPLE_REPORTS = {
    "dark-chocolate": {
        "batch": "DC-260915-03",
        "sugars": [("Lactose", 0.21), ("Glucose", 0.07), ("Galactose", 0.06),
                   ("Maltose", 0.04), ("Sucrose", None), ("Fructose", None)],
    },
    "classic-vanilla": {
        "batch": "CV-260914-02",
        "sugars": [("Lactose", 0.19), ("Glucose", 0.06), ("Galactose", 0.05),
                   ("Maltose", 0.03), ("Sucrose", None), ("Fructose", None)],
    },
    "cookies-and-cream": {
        "batch": "CC-260913-01",
        "sugars": [("Lactose", 0.20), ("Glucose", 0.08), ("Galactose", 0.06),
                   ("Maltose", 0.08), ("Sucrose", None), ("Fructose", None)],
    },
    "strawberry": {
        "batch": "SB-260912-02",
        "sugars": [("Lactose", 0.18), ("Fructose", 0.12), ("Glucose", 0.10),
                   ("Galactose", 0.05), ("Maltose", 0.02), ("Sucrose", None)],
    },
    "alphonso-mango": {
        "batch": "AM-260911-01",
        "sugars": [("Lactose", 0.17), ("Fructose", 0.14), ("Glucose", 0.09),
                   ("Galactose", 0.05), ("Maltose", 0.03), ("Sucrose", 0.01)],
    },
}


def get_sample_report(slug):
    """Return sample results for a product slug, or None if there are none."""
    base = SAMPLE_REPORTS.get(slug)
    if base is None:
        return None
    total = round(sum(v for _, v in base["sugars"] if v), 2)
    return {
        "sample": True,
        "batch": base["batch"],
        "total_sugars": total,
        "limit": SUGAR_LIMIT_G,
        "within_limit": total <= SUGAR_LIMIT_G,
        "fill_percent": min(100, round(total * 100)),  # scale runs 0 to 1 g
        "sugars": base["sugars"],
        "sweeteners": _SWEETENERS,
        "method": "HPLC sugar profile",
        "tested_on": "17 Sep 2026",
        "lab_name": None,
        "accreditation": None,
    }
