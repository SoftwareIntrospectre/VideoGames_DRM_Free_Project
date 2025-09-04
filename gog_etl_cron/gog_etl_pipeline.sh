#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p gog_etl_logs

# Create timestamped log file
LOGFILE="gog_etl_logs/gog_etl_$(date '+%Y-%m-%d_%H-%M-%S').log"

# (Optional) Use a specific Python executable
PYTHON_EXEC="/mnt/c/Users/tchac/Documents/Career/Projects/DataPlatformEngineering/VideoGames_DRM_Free_Project/venv/Scripts/python.exe"

# Use default 'python' if not using the venv
# PYTHON_EXEC="python"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting GOG ETL pipeline..." >> "$LOGFILE"

echo "Start: 02_fetch_gog_games_store_api_data.py" >> "$LOGFILE"
"$PYTHON_EXEC" ./gog_data_etl/02_fetch_gog_games_store_api_data.py >> "$LOGFILE" 2>&1
echo "End:   02_fetch_gog_games_store_api_data.py" >> "$LOGFILE"

echo "Start: 03_load_daily_csv_to_gog_games_staging_table.py" >> "$LOGFILE"
"$PYTHON_EXEC" ./gog_data_etl/03_load_daily_csv_to_gog_games_staging_table.py >> "$LOGFILE" 2>&1
echo "End:   03_load_daily_csv_to_gog_games_staging_table.py" >> "$LOGFILE"

echo "Start: 04_Load_GOG_Staging_to_Fact_Dim_Tables.py" >> "$LOGFILE"
"$PYTHON_EXEC" ./gog_data_etl/04_Load_GOG_Staging_to_Fact_Dim_Tables.py >> "$LOGFILE" 2>&1
echo "End:   04_Load_GOG_Staging_to_Fact_Dim_Tables.py" >> "$LOGFILE"

echo "Start: 05_folder_cleanup.py" >> "$LOGFILE"
"$PYTHON_EXEC" ./gog_data_etl/05_folder_cleanup.py >> "$LOGFILE" 2>&1
echo "End:   05_folder_cleanup.py" >> "$LOGFILE"

echo "$(date '+%Y-%m-%d %H:%M:%S') - GOG ETL pipeline completed successfully!" >> "$LOGFILE"
