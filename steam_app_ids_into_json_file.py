import requests
import json
import os
import logging

# Set up logging
logging.basicConfig(
    filename='./steam_daily_files/steam_app_ids.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# File to store valid app IDs
VALID_APP_IDS_FILE = "./steam_daily_files/valid_app_ids.json"

# Create the directory if it doesn't exist
if not os.path.exists('./steam_daily_files/'):
    os.makedirs('./steam_daily_files/')

def fetch_app_list():
    """Fetch the app list from Steam API."""
    logging.info("Fetching app list from Steam API.")
    
    try:
        response = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/')
        response.raise_for_status()  # Raise an error for bad responses
        app_list = response.json()
        
        logging.info("Successfully fetched app list.")
        return app_list['applist']['apps']

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching app list: {e}")
        return []

def is_valid_app_id(app_id):
    """Check if the app ID is valid by querying the app details."""
    details_url = f'https://store.steampowered.com/api/appdetails?appids={app_id}'
    try:
        response = requests.get(details_url)
        response.raise_for_status()
        details_data = response.json()
        return str(app_id) in details_data and details_data[str(app_id)]['success']
    except requests.exceptions.RequestException as e:
        logging.warning(f"Error checking validity for app ID {app_id}: {e}")
        return False

def extract_valid_app_ids(apps):
    """Extract valid app IDs from the app list."""
    valid_ids = []
    
    for app in apps:
        app_id = app['appid']
        if is_valid_app_id(app_id):
            valid_ids.append(app_id)
            logging.info(f"App ID {app_id} is valid.")
        else:
            logging.info(f"App ID {app_id} is invalid.")

    logging.info(f"Extracted {len(valid_ids)} valid app IDs.")
    return valid_ids

def save_valid_app_ids(app_ids):
    """Save valid app IDs to a JSON file."""
    with open(VALID_APP_IDS_FILE, 'w') as f:
        json.dump(app_ids, f)
    logging.info("Saved valid app IDs to file.")

# Main execution
logging.info("Starting the process to fetch valid app IDs.")
apps = fetch_app_list()
if apps:
    valid_app_ids = extract_valid_app_ids(apps)
    save_valid_app_ids(valid_app_ids)
logging.info("Process completed.")