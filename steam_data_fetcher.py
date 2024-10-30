import requests
import json
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    filename=f"./steam_daily_files/steam_scraper_logger_{datetime.now().strftime('%Y%m%d')}.log", 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define the cache file for app details
CACHE_FILE = './steam_daily_files/app_details_cache.json'

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

def save_cache(data):
    """
        Save the cached app details to the cache file.

        Args:
            data (dict): The app details to cache.
    """
    with open(CACHE_FILE, 'w') as f:
        logging.info(f"saving app_id to CACHE_FILE: {CACHE_FILE}.")
        json.dump(data, f, indent=4)  # Write cached data to the file in JSON format

def fetch_game_details(app_id):
    """
        Fetch game details from the Steam API for a given app ID.

        Args:
            app_id (str): The app ID of the game.

        Returns:
            dict: The game details if successful, otherwise None.
    """
    details_url = f'https://store.steampowered.com/api/appdetails?appids={app_id}'
    
    try:
        details_response = requests.get(details_url)
        details_response.raise_for_status()  # Raise an error for bad responses
        
        details_data = details_response.json()
        if str(app_id) in details_data and details_data[str(app_id)]['success']:
            return details_data[str(app_id)]['data']
        else:
            logging.error(f"App ID {app_id} not found in response.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching details for app ID {app_id}: {e}")
    
    return None

def process_app_ids(app_ids):
    """
        Process each valid app ID to fetch game details and manage caching.

        Args:
            app_ids (set): A set of valid app IDs to process.
    """
    cache = load_cache()  # Load previously cached app details
    new_data = []  # Initialize a list for new app details

    logging.info(f"Processing {len(app_ids)} valid app IDs.")

    for app_id in app_ids:
        if app_id in cache:  # Use cached data if available
            logging.info(f"Using cached data for app ID: {app_id}")
            new_data.append(cache[app_id])
            continue
        
        game_details = fetch_game_details(app_id)
        if game_details:
            cache[app_id] = game_details  # Cache the successful response
            save_cache(cache)  # Save the cache after each successful fetch
            new_data.append(game_details)  # Add the new game details to the list

    return new_data  # Return the list of new game details
