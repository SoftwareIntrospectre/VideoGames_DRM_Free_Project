import subprocess

python_executable = r'C:/Users/tchac/Documents/Career/Projects\DataPlatformEngineering/VideoGames_DRM_Free_Project/venv/Scripts/python.exe'

subprocess.run(['python', 'fetch_gog_games_store_api_data.py'])
subprocess.run(['python', 'gog_games_daily_push_to_mysql.py'])