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

# Define the cache file and output pipe-delimited CSV file
CACHE_FILE = './steam_daily_files/app_details_cache.json'
OUTPUT_CSV_FILE = f"./steam_daily_files/steam_game_details_extracted_{datetime.now().strftime('%Y%m%d')}.csv"

def load_cache():
    """
    Load the cached app details from the cache file.

    Returns:
        dict: A dictionary of cached app details if the cache file exists, 
        otherwise an empty dictionary.
    """
    if os.path.exists(CACHE_FILE):
        logging.info(f"CACHE_FILE: {CACHE_FILE} exists. Loading.")
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)  # Load cached data into a dictionary
    return {}  # Return an empty dictionary if the cache file doesn't exist

def clean_string(s):
    """
    Clean the string by removing double quotes.

    Args:
        s (str): The string to clean.

    Returns:
        str: The cleaned string.
    """
    return s.replace('"', '')

def extract_data_to_csv(cache):
    """
    Extract relevant data from the cache and save it to a pipe-delimited CSV file.

    Args:
        cache (dict): The cached app details.
    """
    new_data = []  # Initialize a list for new app details

    for app_id, game_details in cache.items():
        # Collect relevant data into a dictionary, cleaning string values
        data_entry = {
            "steam_game_id": clean_string(str(game_details['steam_appid'])),
            "steam_game_name": clean_string(game_details['name']),
            "is_free": str(game_details.get('is_free', False)),
            "developer": clean_string(game_details.get('developers', ['N/A'])[0]),
            "publisher": clean_string(game_details.get('publishers', ['N/A'])[0]),
            "genre1_id": clean_string(game_details['genres'][0]['id']) if game_details.get('genres') else 'N/A',
            "genre1_name": clean_string(game_details['genres'][0]['description']) if game_details.get('genres') else 'N/A',
            "release_date": clean_string(game_details.get('release_date', {}).get('date', 'N/A')),
            "required_age": str(game_details.get('required_age', 0)),
            "on_windows_pc_platform": str(game_details.get('platforms', {}).get('windows', False)),
            "on_apple_mac_platform": str(game_details.get('platforms', {}).get('mac', False)),
            "on_linux_platform": str(game_details.get('platforms', {}).get('linux', False))
        }
        new_data.append(data_entry)  # Add the data entry to the list

    # Save the collected data to a pipe-delimited CSV
    df = pd.DataFrame(new_data)
    df.to_csv(OUTPUT_CSV_FILE, index=False, sep='|')
    logging.info(f"Extracted data saved to {OUTPUT_CSV_FILE}")

# Main execution block
if __name__ == "__main__":
    logging.info("Starting data extraction from cache.")  # Log the start of the extraction
    cache = load_cache()  # Load cached app details
    extract_data_to_csv(cache)  # Extract and save data to CSV