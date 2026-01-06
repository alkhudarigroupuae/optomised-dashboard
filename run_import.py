import json
from scrape_omaya import import_to_woocommerce
# Reuse existing WooCommerce credentials from import_cakes to avoid duplication
from import_cakes import WC_URL as WP_URL, WC_CK as CONSUMER_KEY, WC_CS as CONSUMER_SECRET
from woocommerce import API
CAT_NAME = "Omaya Products"
QUIET = True

def load_products(filename="products.json"):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def verify_category_upload(expected_products, cat_name):
    wcapi = API(url=WP_URL, consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, version="wc/v3", timeout=20)
    # Find category ID by name
    category_id = 0
    resp = wcapi.get("products/categories")
    if resp.status_code == 200:
        for cat in resp.json():
            if cat.get("name") == cat_name:
                category_id = cat.get("id")
                break
    if not category_id:
        print(f"Verification: Category '{cat_name}' not found.")
        return
    # Fetch all products in this category
    remote_names = set()
    page = 1
    while True:
        r = wcapi.get("products", params={"category": category_id, "per_page": 100, "page": page})
        if r.status_code != 200:
            print(f"Verification: Failed to fetch products page {page}: {r.status_code}")
            break
        items = r.json()
        if not items:
            break
        for it in items:
            remote_names.add(it.get("name") or "")
        page += 1
    expected_names = set(p.get("name") or "" for p in expected_products)
    missing = expected_names - remote_names
    extra = remote_names - expected_names
    report_lines = []
    report_lines.append(f"Verification Results for '{cat_name}':")
    report_lines.append(f"- Expected: {len(expected_names)}")
    report_lines.append(f"- Found on store: {len(remote_names)}")
    if missing:
        report_lines.append(f"- Missing ({len(missing)}): " + ", ".join(list(missing)[:10]) + (" ..." if len(missing) > 10 else ""))
    else:
        report_lines.append("- Missing: None")
    if extra:
        report_lines.append(f"- Extra in category ({len(extra)}): " + ", ".join(list(extra)[:10]) + (" ..." if len(extra) > 10 else ""))
    else:
        report_lines.append("- Extra in category: None")
    report = "\n".join(report_lines)
    print("\n" + report)

if __name__ == "__main__":
    if not QUIET:
        print("Loading products...")
    products = load_products()
    if not QUIET:
        print(f"Loaded {len(products)} products.")
        print("Starting import...")
    # Process in small batches to improve reliability
    batch_size = 30
    for start in range(0, len(products), batch_size):
        end = start + batch_size
        batch = products[start:end]
        if not QUIET:
            print(f"\nProcessing batch {start}-{end}...")
        import_to_woocommerce(batch, WP_URL, CONSUMER_KEY, CONSUMER_SECRET, cat_name=CAT_NAME, verbose=not QUIET)
    # Verify upload completeness
    try:
        verify_category_upload(products, CAT_NAME)
    except Exception as e:
        print(f"Verification error: {str(e)}")
