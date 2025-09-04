import subprocess

python_executable = r'C:/Users/tchac/Documents/Career/Projects\DataPlatformEngineering/VideoGames_DRM_Free_Project/venv/Scripts/python.exe'

print("Start: '02_fetch_gog_games_store_api_data' Python script")
subprocess.run(['python', './gog_data_etl/02_fetch_gog_games_store_api_data.py'])
print("End: '02_fetch_gog_games_store_api_data' Python script")

print("Start: '03_load_daily_csv_to_gog_games_staging_table' Python script")
subprocess.run(['python', './gog_data_etl/03_load_daily_csv_to_gog_games_staging_table.py'])
print("End: '03_load_daily_csv_to_gog_games_staging_table' Python script")

print("Start: '04_Load_GOG_Staging_to_Fact_Dim_Tables' Python script")
subprocess.run(['python', './gog_data_etl/04_Load_GOG_Staging_to_Fact_Dim_Tables.py'])
print("End: '04_Load_GOG_Staging_to_Fact_Dim_Tables' Python script")

print("Start: '05_folder_cleanup' Python script")
subprocess.run(['python', './gog_data_etl/05_folder_cleanup.py'])
print("End: '05_folder_cleanup' Python script")