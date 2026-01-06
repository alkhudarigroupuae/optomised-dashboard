import json
import time
from woocommerce import API
import os

# WooCommerce API Credentials
WC_URL = "https://mahmoudbey-oc.com/"
WC_CK = "ck_689a9851ae9c92e0afd89199a4b30eec1ab36c0b"
WC_CS = "cs_935a014aa1f232581dc4ae2e0849d66bbc3e52ac"

wcapi = API(
    url=WC_URL,
    consumer_key=WC_CK,
    consumer_secret=WC_CS,
    version="wc/v3",
    timeout=20
)

CATEGORY_NAME = "Cake Category"
CATEGORY_ID = 160  # We know this from previous runs

def import_products():
    print("Loading products from products.json...")
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
        
    print(f"Loaded {len(products)} products.")
    
    # Verify Category
    print(f"Using Category ID: {CATEGORY_ID}")
    
    print("\nStarting import to WooCommerce...")
    success_count = 0
    fail_count = 0
    
    for i, p in enumerate(products):
        try:
            print(f"[{i+1}/{len(products)}] Processing {p['name']}...")
        except UnicodeEncodeError:
            print(f"[{i+1}/{len(products)}] Processing (Name cannot be printed)...")
        
        # Prepare data
        raw_price = p['price'].replace('ل.س', '').replace(',', '').replace('.', '').strip()
        if not raw_price.isdigit():
             raw_price = "0"

        data = {
            "name": p['name'],
            "type": "simple",
            "regular_price": raw_price,
            "description": f"Scraped from Omaya Class. Original Price: {p['price']}",
            "categories": [
                {
                    "id": CATEGORY_ID
                }
            ],
            "images": [
                {
                    "src": p['image_url']
                }
            ]
        }
        
        # Check if product exists
        existing_id = 0
        try:
            # Search by name
            response = wcapi.get("products", params={"search": p['name']})
            if response.status_code == 200:
                found_products = response.json()
                for fp in found_products:
                    if fp['name'] == p['name']:
                        existing_id = fp['id']
                        print(f"  Product already exists (ID: {existing_id}). Updating...")
                        break
        except Exception as e:
            print(f"  Error checking existence: {e}")

        # Create or Update product
        try:
            if existing_id:
                response = wcapi.put(f"products/{existing_id}", data)
                action = "Updated"
            else:
                response = wcapi.post("products", data)
                action = "Created"

            if response.status_code in [200, 201]:
                prod_id = response.json().get('id')
                print(f"  Success! {action} Product ID: {prod_id}")
                success_count += 1
            else:
                print(f"  Failed: {response.status_code} - {response.text}")
                fail_count += 1
        except Exception as e:
            print(f"  Error saving product: {e}")
            fail_count += 1
            
        # Be polite to API
        # time.sleep(0.5)

    print(f"\nImport finished. Success: {success_count}, Failed: {fail_count}")

if __name__ == "__main__":
    import_products()
