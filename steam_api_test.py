import requests
import pandas as pd
from datetime import datetime

# Fetch the list of games
response = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/')
app_list = response.json()

new_data = []
count = 0

# Loop through the first 10 app IDs
for app in app_list['applist']['apps']:
    if count >= 10:
        break

    app_id = app['appid']
    
    # Fetch detailed information for each app using the app ID
    details_response = requests.get(f'https://store.steampowered.com/api/appdetails?appids={app_id}')

    if details_response.status_code == 200:
        details_data = details_response.json()
        
        # Check if the request was successful
        if str(app_id) in details_data and details_data[str(app_id)]['success']:
            game_details = details_data[str(app_id)]['data']

            genre_info = game_details.get('genres', [])

            # Check if the game is paid and not unreleased
            is_free = game_details.get('is_free', False)
            release_date_info = game_details.get('release_date', {}).get('date', '')

            # Adjusting condition for is_free and release date
            if not is_free and release_date_info not in ('Coming soon', None, ''):
                data_entry = {
                    "steam_game_id": game_details['steam_appid'],
                    "steam_game_name": game_details['name'],
                    "developer": game_details.get('developers', ['N/A'])[0],
                    "publisher": game_details.get('publishers', ['N/A'])[0],
                    "release_date": release_date_info,
                    "genre_1_id": genre_info[0]['id'] if genre_info else 'N/A',
                    "genre_1_description": genre_info[0]['description'] if genre_info else 'N/A',
                    "on_windows_pc_platform": game_details.get('platforms', {}).get('windows', False),
                    "on_mac_platform": game_details.get('platforms', {}).get('mac', False),
                    "on_linux_platform": game_details.get('platforms', {}).get('linux', False)
                }
                
                new_data.append(data_entry)
                count += 1

        else:
            print(f"Details not available for app ID {app_id} or success is false.")
    else:
        print(f"Failed to fetch details for app ID {app_id}. Status code: {details_response.status_code}")

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