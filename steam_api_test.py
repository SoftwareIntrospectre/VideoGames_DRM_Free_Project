import requests
import pandas as pd
from datetime import datetime
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# TODO: API limits 100,000 requests per day. Keep that in mind with testing too (Keep in mind I'm doing 2 requests per game)


# Fetch the list of games (need "app ID")
response = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/')
app_list = response.json()

new_data = []
count = 0

# Loop through the first 100 app IDs
for app in app_list['applist']['apps']:
    if count >= 100:
        break

    app_id = app['appid']
    
    # Fetch detailed information for each app using the app ID
    details_response = requests.get(f'https://store.steampowered.com/api/appdetails?appids={app_id}', headers=headers)
    
    if details_response.status_code == 200:
        details_data = details_response.json()
        
        # Check if the request was successful
        if str(app_id) in details_data and details_data[str(app_id)]['success']:
            game_details = details_data[str(app_id)]['data']

            genre_info = game_details.get('genres', [])

            # Check if the game is paid and not unreleased
            is_free = game_details.get('is_free', False)
            release_date_raw = game_details.get('release_date', {}).get('date', None)
            game_type = game_details.get('type', '')

            # Check if the release date is valid
            if release_date_raw and release_date_raw.lower() not in ['to be announced', 'coming soon', '']:
                release_date = pd.to_datetime(release_date_raw, errors='coerce')  # Use errors='coerce' to handle invalid formats
            else:
                release_date = None  # Set to None if it's not a valid date

            # Ignoring cases that aren't relevant
            if is_free or release_date in ('coming soon', 'to be announced', None, '') or game_type == "dlc":
                print(f"app ID: {app_id} is either a free game, not yet released, or DLC. Ignoring.")
                pass

            else:

                pc_requirements = game_details.get('pc_requirements', [])
                mac_requirements = game_details.get('mac_requirements', [])
                linux_requirements = game_details.get('linux_requirements', [])

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
                    "windows_pc_requirements_minimum": pc_requirements[0].get('minimum', '') if isinstance(pc_requirements, list) and len(pc_requirements) > 0 else '',
                    "windows_pc_requirements_recommended": pc_requirements[0].get('recommended', '') if isinstance(pc_requirements, list) and len(pc_requirements) > 0 else '',
                    "apple_mac_requirements_minimum": mac_requirements[0].get('minimum', '') if isinstance(mac_requirements, list) and len(mac_requirements) > 0 else '',
                    "apple_mac_requirements_recommended": mac_requirements[0].get('recommended', '') if isinstance(mac_requirements, list) and len(mac_requirements) > 0 else '',
                    "linux_requirements_minimum": linux_requirements[0].get('minimum', '') if isinstance(linux_requirements, list) and len(linux_requirements) > 0 else '',
                    "linux_requirements_recommended": linux_requirements[0].get('recommended', '') if isinstance(linux_requirements, list) and len(linux_requirements) > 0 else '',
                    "user_rating": game_details.get('content_descriptors', {}).get('ratings', [])
                }
                
                new_data.append(data_entry)
                count += 1
    else:
        print(f"Failed to fetch details for app ID {app_id}. Status code: {details_response.status_code} - '{details_response.reason}'")

# Check if any data was collected before saving
if new_data:
    # Create a DataFrame and save to CSV
    new_df = pd.DataFrame(new_data)
    new_df.to_csv(f"./steam_daily_files/steam_game_details_{datetime.now().strftime('%Y%m%d')}.csv", mode='w', header=True, index=False, sep='|')
else:
    print("No data collected to save.")


'''

        # https://store.steampowered.com/api/appdetails?appids=1824430

        data[type] == game -----------------> always filter to this by default
        data[is_free] == false -------------> always filter to this by default

        steam_game_id = data[steam_appid]
        steam_game_name = game_details[name]
        is_free: true/false
        developer = game_details[developers][0]
        publisher = publishers[0]

        genre1_id = genres[0][id]
        genre1_name = genres[0][description] ---> similar to GOG's Genres

        genre2_id = genres[0][id]
        genre2 = genres[1][description] ---> similar to GOG's Genres
        release_date[date] ----> parse to be a DATETIME

        requiredAge

        on_windows_pc_platform = platforms[windows] (true/false)
        on_apple_mac_platform = platforms[mac] (true/false)
        on_linux_platform = platforms[linux] (true/false)

        windows_pc_requirements_minimum     = pc_requirements[minimum]
        windows_pc_requirements_recommended = pc_requirements[recommended]

        apple_mac_requirements_minimum     = mac_requirements[minimum]
        apple_mac_requirements_recommended = mac_requirements[recommended]

        linux_requirements_minimum = pc_requirements[minimum]
        linux_requirements_recommended = pc_requirements[recommended]

        user_rating = content_descriptors[ratings]

'''