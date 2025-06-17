import requests
import json
from datetime import datetime
from pathlib import Path

# URL to fetch data from
url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
file_path = Path(f"./steam_daily_files/SteamApps_GetAppIDsList_JSON_{datetime.now().strftime('%Y%m%d')}.json")

# Fetch the data
response = requests.get(url)

if response.status_code == 200:

    # Parse the JSON
    data = response.json()

    # Ensure the directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Save to a file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {file_path}")
else:
    print(f"Failed to retrieve data: {response.status_code}")