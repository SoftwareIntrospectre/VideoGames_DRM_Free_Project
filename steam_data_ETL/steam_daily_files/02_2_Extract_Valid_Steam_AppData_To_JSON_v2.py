import requests
import json
import os
import re
from datetime import datetime
import logging
import time

# Set up logging
logging.basicConfig(
    filename=f"./steam_daily_files/steam_extraction_logger_{datetime.now().strftime('%Y%m%d')}.log", 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

CACHE_FILE = './steam_daily_files/app_details_cache.json'
APP_ID_FILE = f"./steam_daily_files/SteamApps_GetAppIDsList_JSON_{datetime.now().strftime('%Y%m%d')}.json"
INVALID_IDS_FILE = './steam_daily_files/invalid_app_ids.txt'

def load_app_ids():
    """Load app IDs from the JSON file."""
    if os.path.exists(APP_ID_FILE):
        with open(APP_ID_FILE, 'r') as f:
            data = json.load(f)
            app_ids = [app['appid'] for app in data['applist']['apps']]
            logging.info(f"Loaded {len(app_ids)} app IDs from {APP_ID_FILE}.")
            return app_ids
    logging.error(f"App ID file {APP_ID_FILE} does not exist.")
    return []

def load_cache():
    """Load the cached app details from the cache file."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logging.warning("Cache file is corrupted. Loading empty cache.")
    return {}

def load_invalid_ids():
    """Load invalid app IDs from a file."""
    if os.path.exists(INVALID_IDS_FILE):
        with open(INVALID_IDS_FILE, 'r') as f:
            invalid_ids = set(line.strip() for line in f)
            logging.info(f"Loaded {len(invalid_ids)} invalid app IDs from {INVALID_IDS_FILE}.")
            return invalid_ids
    return set()

def save_invalid_ids(invalid_ids):
    """Save the set of invalid app IDs to a file."""
    with open(INVALID_IDS_FILE, 'w') as f:
        f.writelines(f"{app_id}\n" for app_id in invalid_ids)
    logging.info(f"Saved {len(invalid_ids)} invalid app IDs to {INVALID_IDS_FILE}.")

def save_cache(cache):
    """Save the valid app details to the cache file."""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=4)
    logging.info(f"Cached {len(cache)} valid app details to {CACHE_FILE}.")

def clean_price(price_str):
    """Extract numeric value from price string."""
    cleaned_price_str = re.sub(r'[^\d.]', '', price_str)
    if cleaned_price_str.count('.') > 1:
        logging.warning(f"Invalid price format detected: {price_str}")
        return 0
    return float(cleaned_price_str) if cleaned_price_str else 0

def process_app_ids(app_ids):
    """Fetch app details and filter valid games."""
    cache = load_cache()
    invalid_ids = load_invalid_ids()
    new_data = {}
    invalid_ids_to_save = set()

    total_apps = len(app_ids)
    logging.info(f"Processing {total_apps} valid app IDs.")

    for count, app_id in enumerate(app_ids, start=1):
        if app_id in cache:
            new_data[app_id] = cache[app_id]
            continue

        if app_id in invalid_ids:
            continue

        details_url = f'https://store.steampowered.com/api/appdetails?appids={app_id}'
        retry_attempts = 0
        max_retries = 5

        while retry_attempts < max_retries:
            try:
                details_response = requests.get(details_url)
                details_response.raise_for_status()
                details_data = details_response.json()

                if str(app_id) in details_data and details_data[str(app_id)]['success']:
                    game_details = details_data[str(app_id)]['data']
                    game_type = game_details.get('                    game_type = game_details.get('type', '')
                    is_free = game_details.get('is_free', False)
                    price_str = game_details.get('price_overview', {}).get('final_formatted', '')

                    price = clean_price(price_str)

                    if game_type != "game" or (is_free or price <= 0):
                        logging.info(f"App ID: {app_id} is not a valid paid game. Marking as invalid.")
                        invalid_ids_to_save.add(app_id)
                        break

                    new_data[app_id] = game_details
                    logging.info(f"Processed app ID: {app_id} ({count}/{total_apps})")
                    break

                else:
                    logging.error(f"App ID {app_id} not found in response.")
                    invalid_ids_to_save.add(app_id)
                    break

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    wait_time = 60 * (2 ** retry_attempts)
                    logging.warning(f"Received 429 Client Error for app ID: {app_id}. Pausing for {wait_time} seconds...")
                    time.sleep(wait_time)
                    retry_attempts += 1
                elif e.response.status_code == 403:
                    wait_time = 30
                    logging.error(f"Received 403 Forbidden for app ID: {app_id}. Pausing for {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                    retry_attempts += 1
                else:
                    logging.error(f"Error fetching details for app ID {app_id}: {e}")
                    break

            except requests.exceptions.RequestException as e:
                logging.error(f"Network error for app ID {app_id}: {e}")
                break

    # Save invalid IDs and cache after processing all app IDs
    if invalid_ids_to_save:
        invalid_ids.update(invalid_ids_to_save)
        save_invalid_ids(invalid_ids)
    if new_data:
        save_cache(new_data)

# Main execution block
if __name__ == "__main__":
    logging.info("Starting to process app IDs.")
    app_ids = load_app_ids()
    invalid_ids = load_invalid_ids()
    app_ids = [app_id for app_id in app_ids if app_id not in invalid_ids]
    logging.info(f"Filtered out {len(invalid_ids)} invalid app IDs. Proceeding with {len(app_ids)} valid app IDs.")
    process_app_ids(app_ids)