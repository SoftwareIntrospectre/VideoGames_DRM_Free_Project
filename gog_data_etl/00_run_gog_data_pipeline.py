import subprocess

python_executable = r'C:/Users/tchac/Documents/Career/Projects\DataPlatformEngineering/VideoGames_DRM_Free_Project/venv/Scripts/python.exe'

print("Start: '01_run_gog_data_pipeline' Python script")
subprocess.run(['python', './gog_data_etl/01_fetch_gog_games_store_api_data.py'])
print("End: '01_run_gog_data_pipeline' Python script")

print("Start: '02_load_daily_csv_to_gog_games_staging_table' Python script")
subprocess.run(['python', './gog_data_etl/02_load_daily_csv_to_gog_games_staging_table.py'])
print("End: '02_load_daily_csv_to_gog_games_staging_table' Python script")


# subprocess.run(['python', 'gog_games_daily_push_to_mysql.py'])