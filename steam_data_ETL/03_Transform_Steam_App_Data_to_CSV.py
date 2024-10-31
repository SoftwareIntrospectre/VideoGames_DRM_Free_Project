import pandas as pd
import json
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    filename=f"./steam_daily_files/steam_extraction_logger_{datetime.now().strftime('%Y%m%d')}.log", 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

CACHE_FILE = './steam_daily_files/app_details_cache.json'
OUTPUT_CSV_FILE = f"./steam_daily_files/steam_game_details_exported_{datetime.now().strftime('%Y%m%d')}.csv"

def load_cache():
    """Load the cached app details from the cache file."""
    if os.path.exists(CACHE_FILE):
        logging.info(f"CACHE_FILE: {CACHE_FILE} exists. Loading.")
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)  # Load cached data into a dictionary
    logging.warning(f"CACHE_FILE: {CACHE_FILE} does not exist.")
    return {}  # Return an empty dictionary if the cache file doesn't exist

def export_to_csv(cache):
    """Transform the cached data into a CSV file."""
    new_data = []  # Initialize a list for new app details

    for app_id, game_details in cache.items():
        # Collect relevant game attributes
        game_type = game_details.get('type', '')
        is_free = game_details.get('is_free', False)
        release_date_raw = game_details.get('release_date', {}).get('date', None)
        price_str = game_details.get('price_overview', {}).get('final_formatted', '').replace('$', '')

        # Attempt to convert the price to a float
        try:
            price = float(price_str) if price_str else 0
        except ValueError:
            price = 0  # If conversion fails, set price to 0

        # Check if it's a valid paid game
        if game_type != "game" or (is_free or price <= 0):
            logging.info(f"app ID: {app_id} is not a valid paid game. Skipping.")
            continue  # Skip processing for invalid games

        if release_date_raw and release_date_raw.lower() in ['to be announced', 'coming soon', '']:
            logging.warning(f"app ID: {app_id} does not have a valid release date. Ignoring.")
            continue  # Skip if the release date is not valid

        # Check if the release date is in the future
        release_date = pd.to_datetime(release_date_raw, errors='coerce')  # Convert to datetime
        if release_date and release_date > datetime.now():
            logging.warning(f"app ID: {app_id} has a future release date ({release_date_raw}). Ignoring.")
            continue  # Skip if the release date is in the future

        # Collect relevant data into a dictionary
        data_entry = {
            "steam_game_id": game_details['steam_appid'],
            "steam_game_name": game_details['name'],
            "price": price,  # Use the float price here
            "developer": game_details.get('developers', ['N/A'])[0],
            "publisher": game_details.get('publishers', ['N/A'])[0],
            "genre1_id": game_details['genres'][0]['id'] if game_details.get('genres') else 'N/A',
            "genre1_name": game_details['genres'][0]['description'] if game_details.get('genres') else 'N/A',
            "release_date": game_details.get('release_date', {}).get('date', 'N/A'),
            "required_age": str(game_details.get('required_age', 0)),
            "on_windows_pc_platform": str(game_details.get('platforms', {}).get('windows', False)),
            "on_apple_mac_platform": str(game_details.get('platforms', {}).get('mac', False)),
            "on_linux_platform": str(game_details.get('platforms', {}).get('linux', False))
        }

        new_data.append(data_entry)  # Add the data entry to the list

    # Save the collected data to a CSV
    df = pd.DataFrame(new_data)
    df = df.fillna('')  # Fill NaNs with empty strings to avoid empty columns
    df.to_csv(OUTPUT_CSV_FILE, index=False)
    logging.info(f"Extracted data saved to {OUTPUT_CSV_FILE}")

# Main execution block
if __name__ == "__main__":
    logging.info("Starting data export from cache.")  # Log the start of the export
    cache = load_cache()  # Load cached app details
    export_to_csv(cache)  # Transform and save data to CSV
