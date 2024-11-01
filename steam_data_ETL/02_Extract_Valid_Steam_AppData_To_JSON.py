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
    """Load app IDs from the JSON file created in Part 1."""
    if os.path.exists(APP_ID_FILE):
        with open(APP_ID_FILE, 'r') as f:
            data = json.load(f)
            app_ids = [app['appid'] for app in data['applist']['apps']]
            logging.info(f"Loaded {len(app_ids)} app IDs from {APP_ID_FILE}.")
            return app_ids
    else:
        logging.error(f"App ID file {APP_ID_FILE} does not exist.")
        return []

def load_cache():
    """Load the cached app details from the cache file."""
    if os.path.exists(CACHE_FILE):
        logging.info(f"CACHE_FILE: {CACHE_FILE} exists. Loading.")
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)  # Load cached data into a dictionary
    return {}  # Return an empty dictionary if the cache file doesn't exist

def load_invalid_ids():
    """Load invalid app IDs from a file."""
    if os.path.exists(INVALID_IDS_FILE):
        with open(INVALID_IDS_FILE, 'r') as f:
            invalid_ids = set(line.strip() for line in f)
            logging.info(f"Loaded {len(invalid_ids)} invalid app IDs from {INVALID_IDS_FILE}.")
            return invalid_ids
    return set()  # Return an empty set if the file doesn't exist

def save_invalid_ids(invalid_ids):
    """Save the set of invalid app IDs to a file."""
    with open(INVALID_IDS_FILE, 'w') as f:
        for app_id in invalid_ids:
            f.write(f"{app_id}\n")
    logging.info(f"Saved {len(invalid_ids)} invalid app IDs to {INVALID_IDS_FILE}.")

def save_cache(cache):
    """Save the valid app details to the cache file."""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=4)
    logging.info(f"Cached {len(cache)} valid app details to {CACHE_FILE}.")

def clean_price(price_str):
    """Extract numeric value from price string."""
    cleaned_price_str = re.sub(r'[^\d.]', '', price_str)  # Remove non-numeric characters, except for '.'
    
    # Check for multiple decimal points and return 0 if invalid
    if cleaned_price_str.count('.') > 1:
        logging.warning(f"Invalid price format detected: {price_str}")
        return 0

    return float(cleaned_price_str) if cleaned_price_str else 0

def process_app_ids(app_ids):
    """Fetch app details and filter valid games."""
    cache = load_cache()  # Load previously cached app details
    invalid_ids = load_invalid_ids()  # Load invalid app IDs
    new_data = {}  # Initialize a dictionary for new app details

    total_apps = len(app_ids)  # Total number of app IDs to process
    logging.info(f"Processing {total_apps} valid app IDs.")

    for count, app_id in enumerate(app_ids, start=1):
        if app_id in cache:  # Use cached data if available
            logging.info(f"Using cached data for app ID: {app_id}")
            new_data[app_id] = cache[app_id]
            continue  # Skip to the next app ID if it’s already cached

        if app_id in invalid_ids:  # Skip invalid app IDs
            logging.info(f"Skipping invalid app ID: {app_id}")
            continue

        # Construct the URL for fetching app details
        details_url = f'https://store.steampowered.com/api/appdetails?appids={app_id}'
        retry_attempts = 0
        max_retries = 5

        while retry_attempts < max_retries:
            try:
                details_response = requests.get(details_url)
                details_response.raise_for_status()  # Raise an error for bad responses

                # Successful response
                details_data = details_response.json()
                if str(app_id) in details_data and details_data[str(app_id)]['success']:
                    game_details = details_data[str(app_id)]['data']
                    
                    # Filter based on game attributes
                    game_type = game_details.get('type', '')
                    is_free = game_details.get('is_free', False)
                    price_str = game_details.get('price_overview', {}).get('final_formatted', '')

                    # Clean and convert the price
                    price = clean_price(price_str)

                    # Check if it's a valid paid game
                    if game_type != "game" or (is_free or price <= 0):
                        logging.info(f"app ID: {app_id} is not a valid paid game. Skipping.")
                        invalid_ids.add(app_id)  # Add to invalid IDs set
                        save_invalid_ids(invalid_ids)  # Save immediately
                        break  # Skip processing for invalid games

                    # Cache valid game details
                    new_data[app_id] = game_details  
                    save_cache(new_data)  # Save the cache after adding each valid game
                    logging.info(f"Processed app ID: {app_id} ({count}/{total_apps})")
                    break  # Exit retry loop on success

                else:
                    logging.error(f"App ID {app_id} not found in response.")
                    invalid_ids.add(app_id)  # Add to invalid IDs set
                    save_invalid_ids(invalid_ids)  # Save immediately
                    break  # Exit if the response doesn't indicate success

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    # Handle 429 error with exponential backoff
                    wait_time = 60 * (2 ** retry_attempts)  # Exponential backoff
                    logging.warning(f"Received 429 Client Error for app ID: {app_id}. Pausing for {wait_time} seconds...")
                    time.sleep(wait_time)  # Pause before retrying
                    retry_attempts += 1
                    continue

                elif e.response.status_code == 403:
                    # Wait and retry for 403 Forbidden error
                    wait_time = 30  # Set a wait time for the 403 error
                    logging.error(f"Received 403 Forbidden for app ID: {app_id}. Pausing for {wait_time} seconds before retrying...")
                    time.sleep(wait_time)  # Pause before retrying
                    retry_attempts += 1
                    continue  # Retry the same app ID

                else:
                    logging.error(f"Error fetching details for app ID {app_id}: {e}")
                    break  # Skip to the next app ID on other errors

            except requests.exceptions.RequestException as e:
                logging.error(f"Network error for app ID {app_id}: {e}")
                break  # Skip to the next app ID on network error


# Main execution block
if __name__ == "__main__":
    logging.info("Starting to process app IDs.")
    app_ids = load_app_ids()  # Load app IDs from Part 1
    # Load invalid IDs after loading app IDs
    invalid_ids = load_invalid_ids()  # Load invalid IDs to skip during API calls
    app_ids = [app_id for app_id in app_ids if app_id not in invalid_ids]  # Filter out invalid app IDs
    logging.info(f"Filtered out {len(invalid_ids)} invalid app IDs. Proceeding with {len(app_ids)} valid app IDs.")
    process_app_ids(app_ids)  # Fetch and filter app details
