import requests
import pandas as pd
from datetime import datetime
import os
import json
import logging
import time

"""
        Steam Game Details Scraper

        This script retrieves game details from the Steam Web API for a list of valid app IDs.
        It logs the process, handles caching of previously fetched data, and manages rate limiting 
        to avoid exceeding API request limits.

        Key Features:
        - Loads valid app IDs from a JSON file.
        - Caches app details in a local JSON file to minimize redundant API requests.
        - Logs important events and errors to a log file.
        - Retrieves game details, including attributes like name, developer, publisher, genre, 
        release date, and platform availability.
        - Saves retrieved game details to a CSV file for further analysis.

        Usage:
        1. Ensure that the Steam Web API key is set in the environment variables.
        2. Prepare a JSON file containing valid app IDs at the specified path.
        3. Run the script to start fetching game details.

        The script is designed to handle potential errors during API requests, such as 
        rate limiting, and retries requests as necessary.
"""

# Set up logging to capture events and errors
logging.basicConfig(
    filename=f"./steam_daily_files/steam_scraper_logger_{datetime.now().strftime('%Y%m%d')}.log", 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load the Steam Web API key from environment variables
# STEAM_WEB_API_KEY = os.getenv('STEAM_WEB_API_KEY')

# Define the file to store valid app IDs and the cache file for app details
VALID_APP_IDS_FILE = "./steam_daily_files/distinct_valid_app_ids.json"
CACHE_FILE = './steam_daily_files/app_details_cache.json'

# Create the directory for storing files if it doesn't exist
if not os.path.exists('./steam_daily_files/'):
    os.makedirs('./steam_daily_files/')

# Set the fetch limit for API requests and the time period for rate limiting
FETCH_LIMIT = 100
TIME_PERIOD = 30  # seconds

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

def load_valid_app_ids():
    """
        Load valid app IDs from the specified file.

        Returns:
            set: A set of valid app IDs, or an empty set if the file doesn't exist or fails to load.
    """
    if os.path.exists(VALID_APP_IDS_FILE):
        with open(VALID_APP_IDS_FILE, 'r') as f:
            try:
                data = json.load(f)  # Load the JSON data
                logging.info(f"Loaded data: {data}")
                return set(data.get("app_ids", []))  # Return the app_ids set
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON: {e}")
    else:
        logging.warning(f"File not found: {VALID_APP_IDS_FILE}")
    return set()  # Return an empty set if the file doesn't exist

def process_app_ids(app_ids):
    """
    Process each valid app ID to fetch game details from the Steam API.

    Args:
        app_ids (set): A set of valid app IDs to process.
    """
    # Define headers for the API request
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    #     'key': STEAM_WEB_API_KEY  # Include the API key in the headers
    # }

    cache = load_cache()  # Load any previously cached app details
    new_data = []  # Initialize a list to collect new app details
    total_apps = len(app_ids)  # Count the total number of app IDs to process

    logging.info(f"Processing {total_apps} valid app IDs.")

    request_count = 0  # Counter for the number of API requests made
    start_time = time.time()  # Record the start time for rate limiting
    
    # Define the path for the CSV file to save game details
    csv_file_path = f"./steam_daily_files/steam_game_details_{datetime.now().strftime('%Y%m%d')}.csv"

    # Iterate over each app ID
    for count, app_id in enumerate(app_ids, start=1):
        if app_id in cache:  # Check if the app ID is already cached
            logging.info(f"Using cached data for app ID: {app_id}")
            game_details = cache[app_id]  # Retrieve cached data
        else:
            # Construct the URL for fetching app details from the Steam API
            details_url = f'https://store.steampowered.com/api/appdetails?appids={app_id}'
            while True:  # Loop to handle retries for API requests
                try:
                    details_response = requests.get(details_url)#), headers=headers)  # Make the API request
                    details_response.raise_for_status()  # Raise an error for bad responses

                    # Check for rate limiting (HTTP 429)
                    if details_response.status_code == 429:
                        logging.warning(f"Received 429 Client Error for app ID: {app_id}. Pausing for 60 seconds...")
                        time.sleep(60)  # Pause for 60 seconds if rate limited
                        continue  # Retry the request

                    details_data = details_response.json()  # Parse the response as JSON
                    if str(app_id) in details_data and details_data[str(app_id)]['success']:
                        game_details = details_data[str(app_id)]['data']  # Extract game details
                        
                        # Get game attributes
                        game_type = game_details.get('type', '')  # Game type (e.g., game, dlc, etc.)
                        is_free = game_details.get('is_free', False)  # Check if the game is free
                        release_date_raw = game_details.get('release_date', {}).get('date', None)  # Raw release date

                        # Check if it's a valid paid game
                        if game_type != "game" or is_free:  
                            logging.info(f"app ID: {app_id} is not a valid paid game. Skipping.")
                            break  # Skip processing for invalid games

                        if release_date_raw and release_date_raw.lower() in ['to be announced', 'coming soon', '']:
                            logging.warning(f"app ID: {app_id} does not have a valid release date. Ignoring.")
                            break  # Skip if the release date is not valid

                        release_date = pd.to_datetime(release_date_raw, errors='coerce')  # Convert release date to datetime
                        cache[app_id] = game_details  # Cache the successful response
                        save_cache(cache)  # Save the cache after each successful fetch

                        # Collect relevant data into a dictionary
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

                        new_data.append(data_entry)  # Add the data entry to the list

                        # Write the new data entry to the CSV file
                        new_df = pd.DataFrame([data_entry])  # Create a DataFrame for the new entry
                        new_df.to_csv(csv_file_path, mode='a', header=not os.path.exists(csv_file_path), index=False, sep='|')
                        logging.info(f"Processed app ID: {app_id} ({count}/{total_apps})")
                        break  # Exit the while loop after processing successfully

                    else:
                        break  # Exit if the response doesn't indicate success

                except requests.exceptions.RequestException as e:  # Handle any request exceptions
                    logging.error(f"Error fetching details for app ID {app_id}: {e}")
                    break  # Skip to the next app ID on error

        # Rate limiting logic to avoid hitting API limits
        request_count += 1  # Increment the request count
        if request_count >= FETCH_LIMIT:  # Check if the request limit has been reached
            elapsed_time = time.time() - start_time  # Calculate elapsed time since the last reset
            if elapsed_time < TIME_PERIOD:  # If within the time period
                time_to_wait = TIME_PERIOD - elapsed_time  # Calculate how long to wait
                logging.info(f"Rate limit reached. Waiting for {time_to_wait:.2f} seconds.")
                time.sleep(time_to_wait)  # Wait for the calculated time
            request_count = 0  # Reset the request count
            start_time = time.time()  # Reset the start time

    logging.info("Scraper execution completed.")  # Log completion of the scraping process

# Main execution block
if __name__ == "__main__":
    logging.info("Starting the Steam scraper.")  # Log the start of the scraper
    valid_app_ids = load_valid_app_ids()  # Load valid app IDs from file
    process_app_ids(valid_app_ids)  # Process the valid app IDs to fetch details
