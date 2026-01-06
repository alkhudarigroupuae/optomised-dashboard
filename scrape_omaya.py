import requests
from bs4 import BeautifulSoup
import json
import os
import csv
from urllib.parse import urljoin, urlparse

# Try importing WooCommerce, if not available, we'll skip that part or warn
try:
    from woocommerce import API
    WOOCOMMERCE_AVAILABLE = True
except ImportError:
    WOOCOMMERCE_AVAILABLE = False

BASE_URL = "https://omayaclass.com"
TARGET_URL = "https://omayaclass.com/Products/103/Ar"
IMAGE_DIR = "downloaded_images"
VERBOSE = False
GENERATE_CSV = False

def scrape_products():
    all_products = []
    seen_urls = set()
    page = 1
    
    while True:
        # Construct URL for pagination
        # Based on user input ".../5/Ar/1", we assume path-based pagination: /1, /2, etc.
        url = f"{TARGET_URL}/{page}"
        if VERBOSE:
            print(f"Fetching {url}...")
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch page {page}: {e}")
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all product blocks
        product_blocks = soup.find_all('div', class_='block-stl2')
        if not product_blocks:
            if VERBOSE:
                print("No products found on this page. Stopping.")
            break
            
        if VERBOSE:
            print(f"Found {len(product_blocks)} products on page {page}.")
        
        products_on_page = []
        for block in product_blocks:
            try:
                # Extract Name
                name_tag = block.find('div', class_='text-block').find('h3')
                name = name_tag.get_text(strip=True) if name_tag else "Unknown Product"
                
                # Extract Price
                price_tag = block.find('p', class_='price').find('span')
                price_text = price_tag.get_text(strip=True) if price_tag else "0"
                
                # Extract Product Link (for uniqueness)
                link_tag = block.find('div', class_='btn-sec').find('a', class_='btn4')
                product_link = link_tag.get('href') if link_tag else ""
                
                # Extract Image
                img_tag = block.find('div', class_='img-holder').find('img')
                img_src = img_tag.get('src') if img_tag else ""
                
                # Fix Image URL
                if img_src.startswith('.'):
                    img_src = img_src[1:] # remove the dot
                
                if img_src and not img_src.startswith('http'):
                    full_img_url = urljoin(BASE_URL, img_src)
                else:
                    full_img_url = img_src
                    
                product = {
                    "name": name,
                    "price": price_text,
                    "image_url": full_img_url,
                    "original_image_path": img_src,
                    "product_link": product_link
                }
                
                # Check for duplicates based on Product Link (or Name if link missing)
                unique_key = product_link if product_link else name
                if unique_key in seen_urls:
                    continue
                    
                seen_urls.add(unique_key)
                products_on_page.append(product)
                # print(f"Scraped: {name} - {price_text}")
                
            except AttributeError as e:
                print(f"Error parsing a block: {e}")
                continue

        if not products_on_page:
            if VERBOSE:
                print("No new products found (all duplicates). Stopping.")
            break
            
        all_products.extend(products_on_page)
        if VERBOSE:
            print(f"Added {len(products_on_page)} new products from page {page}.")
        
        # Stop if we found fewer products than expected for a full page (assuming ~16 is full)
        # or just increment and let the duplicate check handle it.
        # But to be safe against infinite loops if the site returns random products:
        if len(products_on_page) == 0:
            break
            
        page += 1

    return all_products

import time
import sys
import concurrent.futures
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

def build_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1280,1024")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)

def enrich_single_product(args):
    i, p = args
    link = p.get('product_link')
    if not link:
        return p
        
    full_link = urljoin(BASE_URL, link)
    if VERBOSE:
        print(f"[{i+1}] Visiting {full_link}...")
    
    try:
        response = requests.get(full_link, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        if response.status_code != 200:
            print(f"Failed to load detail page: {response.status_code}")
            return p
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. Try to find High-Res Image (folder 'larg')
        large_img = soup.find('img', src=lambda x: x and 'larg' in x)
        if large_img:
            large_src = large_img.get('src')
            if large_src.startswith('.'):
                large_src = large_src[1:]
            
            full_large_url = urljoin(BASE_URL, large_src)
            # print(f"  Found Large Image: {full_large_url}")
            p['image_url'] = full_large_url
            p['original_image_path'] = large_src

        # 2. Try to find Name if missing
        if not p['name'] or p['name'] == "Unknown Product":
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                p['name'] = og_title.get('content').strip()
            else:
                page_title = soup.title.string if soup.title else ""
                if page_title and "|" in page_title:
                    p['name'] = page_title.split('|')[0].strip()

        # 3. Try to find Price if missing
        if not p['price'] or p['price'] == "0":
            price_tag = soup.find(class_='price')
            if price_tag:
                price_span = price_tag.find('span')
                if price_span:
                    p['price'] = price_span.get_text(strip=True)

        # Final Fallback
        if not p['name'] or p['name'] == "Unknown Product":
            try:
                prod_id = full_link.split('/')[-2]
                p['name'] = f"Cake Product {prod_id}"
                if VERBOSE:
                    print(f"Assigned Fallback Name: {p['name']}")
            except:
                p['name'] = f"Cake Product {i+1}"

        if not p['price']:
            p['price'] = "0"
            
    except Exception as e:
        if VERBOSE:
            print(f"Error enriching product {link}: {e}")
        
    return p

def dynamic_enrich_product(p, driver):
    link = p.get('product_link')
    if not link:
        return p
    full_link = urljoin(BASE_URL, link)
    try:
        driver.get(full_link)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".text-block, .product-block"))
        )
        name_el = None
        try:
            name_el = driver.find_element(By.CSS_SELECTOR, ".text-block h3")
        except:
            try:
                name_el = driver.find_element(By.CSS_SELECTOR, "h1, h2, h3")
            except:
                name_el = None
        price_el = None
        try:
            price_el = driver.find_element(By.CSS_SELECTOR, "p.price span")
        except:
            price_el = None
        if name_el:
            name_text = name_el.text.strip()
            if name_text:
                p["name"] = name_text
        if price_el:
            price_text = price_el.text.strip()
            if price_text:
                p["price"] = price_text
        if (not p.get("image_url")) or ("larg" not in p.get("image_url","")):
            try:
                img_el = driver.find_element(By.CSS_SELECTOR, "img[src*='larg']")
                src = img_el.get_attribute("src")
                if src:
                    p["image_url"] = src
                    parsed = urlparse(src)
                    p["original_image_path"] = parsed.path
            except:
                pass
        if not p.get("name") or p["name"] == "Unknown Product":
            try:
                prod_id = full_link.split("/")[-2]
                p["name"] = f"Cake Product {prod_id}"
            except:
                p["name"] = p.get("name") or "Cake Product"
        if not p.get("price"):
            p["price"] = "0"
    except Exception as e:
        p["price"] = p.get("price") or "0"
        if not p.get("name"):
            try:
                prod_id = full_link.split("/")[-2]
                p["name"] = f"Cake Product {prod_id}"
            except:
                p["name"] = "Cake Product"
    return p

def enrich_products(products):
    if VERBOSE:
        print(f"Enriching {len(products)} products with details")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Pass index and product as tuple
        args_list = [(i, p) for i, p in enumerate(products)]
        results = list(executor.map(enrich_single_product, args_list))
    if SELENIUM_AVAILABLE:
        try:
            driver = build_driver()
            for i in range(len(results)):
                p = results[i]
                if (not p.get("name") or p["name"] == "Unknown Product") or (not p.get("price") or p["price"] == "0"):
                    results[i] = dynamic_enrich_product(p, driver)
        finally:
            try:
                driver.quit()
            except:
                pass
    return results

def download_image(url, folder):
    if not url:
        return None
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Extract filename from URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename:
            filename = "unknown_image.jpg"
            
        filepath = os.path.join(folder, filename)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return filepath
    except Exception as e:
        if VERBOSE:
            print(f"Error downloading image {url}: {e}")
        return None

def save_to_json(products, filename="products.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    if VERBOSE:
        print(f"Saved {len(products)} products to {filename}")

def save_to_csv(products, filename="products.csv", category_name="Waffle & Crepe"):
    fieldnames = ["Name", "Type", "Regular price", "Description", "Categories", "Images"]
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in products:
            raw_price = p.get('price', '').replace('ل.س', '').replace(',', '').replace('.', '').strip()
            if not raw_price.isdigit():
                raw_price = "0"
            writer.writerow({
                "Name": p.get('name') or "",
                "Type": "simple",
                "Regular price": raw_price,
                "Description": f"Scraped from Omaya Class. Original Price: {p.get('price','')}",
                "Categories": category_name,
                "Images": p.get('image_url') or ""
            })
    if VERBOSE:
        print(f"Saved {len(products)} products to {filename}")
def import_to_woocommerce(products, url, consumer_key, consumer_secret, cat_name="Cake", cat_id=None, verbose=False):
    if not WOOCOMMERCE_AVAILABLE:
        print("WooCommerce library not installed. Please install it.")
        return

    wcapi = API(
        url=url,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        version="wc/v3",
        timeout=20
    )

    category_id = 0 if cat_id is None else cat_id
    
    if category_id == 0:
        if verbose:
            print(f"Checking for category '{cat_name}'...")
        try:
            response = wcapi.get("products/categories")
            if response.status_code == 200:
                categories = response.json()
                for cat in categories:
                    if cat['name'] == cat_name:
                        category_id = cat['id']
                        if verbose:
                            print(f"Found existing category ID: {category_id}")
                        break
            
            if category_id == 0:
                if verbose:
                    print(f"Category '{cat_name}' not found. Creating...")
                cat_data = {"name": cat_name}
                response = wcapi.post("products/categories", cat_data)
                if response.status_code == 201:
                    category_id = response.json().get('id')
                    if verbose:
                        print(f"Created new category ID: {category_id}")
                elif response.status_code == 400 and response.json().get('code') == 'term_exists':
                    category_id = response.json().get('data', {}).get('resource_id', 0)
                    if verbose:
                        print(f"Category already exists. Using ID: {category_id}")
                else:
                    if verbose:
                        print(f"Failed to create category: {response.text}")
        except Exception as e:
            if verbose:
                print(f"Error managing category: {e}")

    created_count = 0
    updated_count = 0
    failed_count = 0
    if verbose:
        print("Starting import to WooCommerce...")
    for p in products:
        # if not p['name']:
        #     print(f"Skipping product with empty name: {p.get('product_link')}")
        #     continue
            
        # Prepare data
        # Note: Price format might need cleaning (remove 'ل.س' and commas)
        # Assuming price is integer for WooCommerce usually, but string is okay if formatted correctly.
        # Removing non-numeric chars except dot if any, but SyP usually has no decimals or uses commas for thousands.
        # "27,000 ل.س" -> "27000"
        raw_price = p['price'].replace('ل.س', '').replace(',', '').replace('.', '').strip()
        
        # Ensure we have a valid price
        if not raw_price.isdigit():
             # Fallback or keep as is if it fails logic
             if verbose:
                 print(f"Warning: Could not parse price '{p['price']}', using 0")
             raw_price = "0"

        # Sanitize image URL (WooCommerce rejects unknown extensions)
        img_url = p.get('image_url') or ""
        try:
            parsed = urlparse(img_url)
            _, ext = os.path.splitext(parsed.path)
            if ext.lower() not in {".jpg", ".jpeg", ".png"}:
                img_url = urljoin(BASE_URL, "/img/uploads1/larg/prod_deff.jpg")
        except Exception:
            img_url = urljoin(BASE_URL, "/img/uploads1/larg/prod_deff.jpg")

        data = {
            "name": p['name'],
            "type": "simple",
            "regular_price": raw_price,
            "description": f"Scraped from Omaya Class. Original Price: {p['price']}",
            "categories": [
                {
                    "id": category_id
                }
            ],
            "images": [
                {
                    "src": img_url
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
                        if verbose:
                            print(f"Product '{p['name']}' already exists (ID: {existing_id}). Updating...")
                        break
        except Exception as e:
            if verbose:
                print(f"Error checking existence: {e}")

        # Create or Update product
        try:
            if existing_id:
                response = wcapi.put(f"products/{existing_id}", data)
                action = "Updated"
            else:
                response = wcapi.post("products", data)
                action = "Created"

            if response.status_code in [200, 201]:
                if action == "Created":
                    created_count += 1
                else:
                    updated_count += 1
                if verbose:
                    print(f"Success! {action} Product ID: {response.json().get('id')}")
            else:
                failed_count += 1
                if verbose:
                    print(f"Failed: {response.status_code} - {response.text}")
        except Exception as e:
            failed_count += 1
            if verbose:
                print(f"Error saving product: {e}")
    if not verbose:
        print(f"Import summary -> Created: {created_count}, Updated: {updated_count}, Failed: {failed_count}")

if __name__ == "__main__":
    try:
        products = scrape_products()
        
        # Enrich with details from product pages
        products = enrich_products(products)
        
        save_to_json(products)
        if GENERATE_CSV:
            save_to_csv(products, filename="products.csv", category_name="Category")
        if VERBOSE:
            print("Scraper Finished")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
