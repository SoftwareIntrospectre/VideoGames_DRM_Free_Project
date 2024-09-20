import pandas as pd
import os
import requests
from datetime import datetime

BASE_URL = "https://catalog.gog.com/v1/catalog"  # Adjust as needed
BATCH_SIZE = 48

def get_total_products():
    response = requests.get(BASE_URL, params={"limit": 1})
    data = response.json()

    if 'productCount' in data:
        return data['productCount']
    else:
        raise ValueError("Could not find total product count.")

def fetch_products(page):
    params = {
        "limit": BATCH_SIZE,
        "order": "desc:trending",
        "productType": "in:game,pack,dlc,extras",
        "page": page
    }
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        return response.json().get("products", [])
    else:
        print(f"Failed to fetch data for page {page}")
        return []

def append_to_csv(products, csv_filename):
    new_data = []  # List to hold data for each product
    for product in products:
        data_entry = {
            "id": product.get('id'),  # Product ID
            "title": product.get('title'),  # Product title
            "releaseDate": format_date(product.get('releaseDate')),  # Formatted release date
            "storeReleaseDate": format_date(product.get('storeReleaseDate')),  # Formatted store release date
            "FinalPrice": clean_price(safe_get_price(product, 'final')),  # Cleaned final price
            "OriginalPrice": clean_price(safe_get_price(product, 'base')),  # Cleaned original price
            "PriceDiscountPercentage": clean_discount(safe_get_discount(product)),  # Cleaned discount percentage
            "PriceDiscountAmount": safe_get_discount_amount(product),  # Discount amount
            "PriceCurrency": safe_get_currency(product),  # Currency
            "productState": product.get('productState'),  # Product state
            "storeLink": product.get('storeLink')  # Product store link
        }

        # Dynamically add Developer, Publisher, OperatingSystem, and Tag columns
        add_dynamic_columns(data_entry, product, 'developers', 'Developer')
        add_dynamic_columns(data_entry, product, 'publishers', 'Publisher')
        add_dynamic_columns(data_entry, product, 'operatingSystems', 'OperatingSystem')
        add_dynamic_columns(data_entry, product, 'tags', 'Tag', key_sub='slug')  # Use slug for tags

        new_data.append(data_entry)  # Add the product's data to the list

    new_df = pd.DataFrame(new_data)  # Create a DataFrame from the list of product data

    # Append to CSV with pipe delimiter
    if os.path.isfile(csv_filename):
        new_df.to_csv(csv_filename, mode='a', header=False, index=False, sep='|')  # Append data if file exists
    else:
        new_df.to_csv(csv_filename, mode='w', header=True, index=False, sep='|')  # Create a new file with headers

def add_dynamic_columns(data_entry, product, key, prefix, key_sub=None):
    """Dynamically add columns for Developers, Publishers, Operating Systems, and Tags."""
    items = product.get(key, [])
    if items:  # Only proceed if there are items
        for i, item in enumerate(items):
            column_name = f"{prefix}{i + 1}"
            data_entry[column_name] = item.get(key_sub) if key_sub else item  # Use key_sub if provided

def format_date(date_str):
    """Convert date string to YYYY-MM-DD format, or return None if invalid."""
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y.%m.%d").strftime("%Y-%m-%d")
        except ValueError:
            return None
    return None

def clean_price(price):
    """Remove dollar sign from price and convert to float, or return None."""
    if price:
        return float(price.replace('$', '').strip())
    return None

def safe_get_price(product, price_type):
    """Safely get price type from product, returning None if not available."""
    price_info = product.get('price')
    return price_info.get(price_type) if price_info else None

def clean_discount(discount):
    """Remove percentage sign from discount and convert to float, or return None."""
    if discount:
        return float(discount.replace('%', '').strip())
    return None

def safe_get_discount(product):
    """Safely get discount percentage from product, returning None if not available."""
    price_info = product.get('price')
    return price_info.get('discount') if price_info else None

def safe_get_discount_amount(product):
    """Safely get discount amount from product, returning None if not available."""
    price_info = product.get('price')
    if price_info and 'finalMoney' in price_info:
        return price_info['finalMoney'].get('discount', None)
    return None

def safe_get_currency(product):
    """Safely get currency from product, returning None if not available."""
    price_info = product.get('price')
    if price_info and 'finalMoney' in price_info:
        return price_info['finalMoney'].get('currency', None)
    return None

def main():
    csv_filename = f"GOG_Games_List_{datetime.now().strftime('%Y%m%d')}.csv"
    total_products = get_total_products()
    
    for page in range(1, (total_products // BATCH_SIZE) + 2):
        products = fetch_products(page)
        append_to_csv(products, csv_filename)  # Append fetched products to the CSV

if __name__ == "__main__":
    main()  # Run the scraper
