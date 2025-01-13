import subprocess

python_executable = r'C:/Users/tchac/Documents/Career/Projects\DataPlatformEngineering/VideoGames_DRM_Free_Project/venv/Scripts/python.exe'

subprocess.run(['python', '01_fetch_gog_games_store_api_data.py'])
subprocess.run(['python', '02_load_daily_csv_to_gog_games_staging_table.py'])
# subprocess.run(['python', 'gog_games_daily_push_to_mysql.py'])