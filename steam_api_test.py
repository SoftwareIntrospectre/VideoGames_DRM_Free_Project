import requests
import pandas as pd
from datetime import datetime
import os
import json
import logging
import time

# Set up logging
logging.basicConfig(
    filename='./steam_daily_files/steam_scraper.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# File to store valid app IDs
VALID_APP_IDS_FILE = "./steam_daily_files/valid_app_ids.json"

if not os.path.exists('./steam_daily_files/'):
    os.makedirs('./steam_daily_files/')

FETCH_LIMIT = 100
TIME_PERIOD = 30  # seconds

# # Load existing valid app IDs from file
# def load_valid_app_ids():
#     sure = [216938, 660010, 660130, 1118314, 1275822, 1343832, 1828741, 1888160, 662172, 1360782, 1820332, 1927051]
#     return set(sure)

# Load existing valid app IDs from file
def load_valid_app_ids():
    if os.path.exists(VALID_APP_IDS_FILE):
        with open(VALID_APP_IDS_FILE, 'r') as f:
            return set(json.load(f))  # Use a set for quick lookup
    return set()

# Process each valid app ID
def process_app_ids(app_ids):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    new_data = []
    total_apps = len(app_ids)
    logging.info(f"Processing {total_apps} valid app IDs.")

    request_count = 0
    start_time = time.time()
    
    csv_file_path = f"./steam_daily_files/steam_game_details_{datetime.now().strftime('%Y%m%d')}.csv"

    for count, app_id in enumerate(app_ids, start=1):
        details_url = f'https://store.steampowered.com/api/appdetails?appids={app_id}'
        
        while True:
            try:
                details_response = requests.get(details_url, headers=headers)
                details_response.raise_for_status()

                if details_response.status_code == 429:
                    logging.warning(f"Received 429 Client Error for app ID: {app_id}. Pausing for 60 seconds...")
                    time.sleep(60)  # Pause for 60 seconds
                    continue  # Retry the request

                details_data = details_response.json()
                if str(app_id) in details_data and details_data[str(app_id)]['success']:
                    game_details = details_data[str(app_id)]['data']
                    
                    is_free = game_details.get('is_free', False)
                    release_date_raw = game_details.get('release_date', {}).get('date', None)
                    game_type = game_details.get('type', '')

                    if release_date_raw and release_date_raw.lower() not in ['to be announced', 'coming soon', '']:
                        release_date = pd.to_datetime(release_date_raw, errors='coerce')
                    else:
                        logging.warning(f"app ID: {app_id} does not have a valid release date. Ignoring.")
                        break

                    if is_free:
                        logging.warning(f"app ID: {app_id} is a free game. Ignoring.")
                        break

                    if is_free or game_type == "dlc":
                        logging.warning(f"app ID: {app_id} is Downloadable Content (DLC). Ignoring.")
                        break

                    elif is_free or game_type == "demo":
                        logging.warning(f"app ID: {app_id} is a demo. Ignoring.")
                        break

                    else:
                        # Collect data
                        data_entry = {
                            "steam_game_id": game_details['steam_appid'],
                            "steam_game_name": game_details['name'],
                            "is_free": is_free,
                            "developer": game_details.get('developers', ['N/A'])[0],
                            "publisher": game_details.get('publishers', ['N/A'])[0],
                            "genre1_id": game_details['genres'][0]['id'] if game_details.get('genres') else 'N/A',
                            "genre1_name": game_details['genres'][0]['description'] if game_details.get('genres') else 'N/A',
                            "genre2_id": game_details['genres'][1]['id'] if len(game_details.get('genres', [])) > 1 else 'N/A',
                            "genre2_name": game_details['genres'][1]['description'] if len(game_details.get('genres', [])) > 1 else 'N/A',
                            "release_date": release_date,
                            "required_age": game_details.get('required_age', 0),
                            "on_windows_pc_platform": game_details.get('platforms', {}).get('windows', False),
                            "on_apple_mac_platform": game_details.get('platforms', {}).get('mac', False),
                            "on_linux_platform": game_details.get('platforms', {}).get('linux', False),
                        }
                        
                        new_data.append(data_entry)

                        # Write to CSV after every 100 records
                        if len(new_data) >= 100:
                            new_df = pd.DataFrame(new_data)
                            new_df.to_csv(csv_file_path, mode='a', header=not os.path.exists(csv_file_path), index=False, sep='|')
                            logging.info(f"Saved {len(new_data)} records to CSV.")
                            new_data.clear()  # Clear the list after saving

                        logging.info(f"Processed app ID: {app_id} ({count}/{total_apps})")
                    break  # Exit the while loop if processing is successful

            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching details for app ID {app_id}: {e}")
                break  # Skip to the next app ID

        # Rate limiting logic
        request_count += 1
        if request_count >= FETCH_LIMIT:
            elapsed_time = time.time() - start_time
            if elapsed_time < TIME_PERIOD:
                time_to_wait = TIME_PERIOD - elapsed_time
                logging.info(f"Rate limit reached. Waiting for {time_to_wait:.2f} seconds.")
                time.sleep(time_to_wait)
            request_count = 0
            start_time = time.time()

    # Save any remaining data
    if new_data:
        new_df = pd.DataFrame(new_data)
        new_df.to_csv(csv_file_path, mode='a', header=not os.path.exists(csv_file_path), index=False, sep='|')
        logging.info(f"Saved {len(new_data)} remaining records to CSV.")

# Main execution
logging.info("Starting the Steam scraper.")
valid_app_ids = load_valid_app_ids()
process_app_ids(valid_app_ids)  # Process the valid app IDs
logging.info("Scraper execution completed.")
