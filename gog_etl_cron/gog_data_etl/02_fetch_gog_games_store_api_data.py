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
        "order": "asc:alphabetical",
        "productType": "in:game",#,pack,dlc,extras",
        "page": page
    }
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        return response.json().get("products", [])
    else:
        print(f"Failed to fetch data for page {page}. Status Code: {response.status_code}, Message: {response.text}")
        return []

def append_to_csv(products, csv_filename):
    new_data = []  # List to hold data for each product
    for product in products:
        data_entry = {
            "id": product.get('id'),  # No caret wrapping
            "title": product.get('title'),  # No caret wrapping
            "releaseDate": format_date(product.get('releaseDate')),
            "storeReleaseDate": format_date(product.get('storeReleaseDate')),
            "FinalPrice": clean_price(safe_get_price(product, 'final')),
            "OriginalPrice": clean_price(safe_get_price(product, 'base')),
            "PriceDiscountPercentage": clean_discount(safe_get_discount(product)),
            "PriceDiscountAmount": safe_get_discount_amount(product),
            "PriceCurrency": safe_get_currency(product),
            "productState": product.get('productState'),
            "storeLink": product.get('storeLink'),
            "Developer": product.get('developers', [None])[0],
            "Publisher": product.get('publishers', [None])[0],
            "OperatingSystem1": product.get('operatingSystems')[0] if len(product.get('operatingSystems', [])) > 0 else None,
            "OperatingSystem2": product.get('operatingSystems')[1] if len(product.get('operatingSystems', [])) > 1 else None,
            "OperatingSystem3": product.get('operatingSystems')[2] if len(product.get('operatingSystems', [])) > 2 else None,
            "Tag1": product.get('tags')[0] if len(product.get('tags', [])) > 0 else None,
            "Tag2": product.get('tags')[1] if len(product.get('tags', [])) > 1 else None,
            "Tag3": product.get('tags')[2] if len(product.get('tags', [])) > 2 else None,
            "Tag4": product.get('tags')[3] if len(product.get('tags', [])) > 3 else None,
            "Tag5": product.get('tags')[4] if len(product.get('tags', [])) > 4 else None,
            "Tag6": product.get('tags')[5] if len(product.get('tags', [])) > 5 else None,
            "Tag7": product.get('tags')[6] if len(product.get('tags', [])) > 6 else None,
            "Tag8": product.get('tags')[7] if len(product.get('tags', [])) > 7 else None,
            "Tag9": product.get('tags')[8] if len(product.get('tags', [])) > 8 else None,
            "Tag10": product.get('tags')[9] if len(product.get('tags', [])) > 9 else None

            # features=single
            # features=multi
            # <a class="details__link ng-scope" href"/games/strategy" [...] </a>
            # <span class="howlongtobeat-box__name" -------> howlong to beat: Main: 50, Main + Sides: 58 h, Completionist: 101.5 h, All Styles: 64.5 h
                    # available on GOG.com. Good information to use.
        }

        new_data.append(data_entry)

    new_df = pd.DataFrame(new_data)

    if os.path.isfile(csv_filename):
        new_df.to_csv(csv_filename, mode='a', header=False, index=False, sep='|')
    else:
        new_df.to_csv(csv_filename, mode='w', header=True, index=False, sep='|')

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
    csv_filename = f"./gog_daily_files/GOG_Games_List_{datetime.now().strftime('%Y%m%d')}.csv"
    total_products = get_total_products()
    
    for page in range(1, (total_products // BATCH_SIZE) + 2):
        print('adding new page')
        products = fetch_products(page)
        append_to_csv(products, csv_filename)  # Append fetched products to the CSV

if __name__ == "__main__":
    main()  # Run the script
