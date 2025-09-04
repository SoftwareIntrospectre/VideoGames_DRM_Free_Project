#!/bin/bash

cd /mnt/c/Users/tchac/Documents/Career/Projects/DataPlatformEngineering/VideoGames_DRM_Free_Project/steam_etl_cron

# Create logs directory if it doesn't exist
mkdir -p steam_etl_logs

# Timestamped log file
LOGFILE="steam_etl_logs/steam_etl_$(date '+%Y-%m-%d_%H-%M-%S').log"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting Steam ETL pipeline..." >> "$LOGFILE"

python ../steam_data_ETL/01_run_steam_data_pipeline.py >> "$LOGFILE" 2>&1
python ../steam_data_ETL/02_Extract_Steam_AppIDs_To_JSON.py >> "$LOGFILE" 2>&1
python ../steam_data_ETL/03_Extract_Valid_Steam_AppData_To_JSON.py >> "$LOGFILE" 2>&1
python ../steam_data_ETL/04_Transform_Steam_App_Data_to_CSV.py >> "$LOGFILE" 2>&1
python ../steam_data_ETL/05_Load_CSV_to_Steam_Staging_Table.py >> "$LOGFILE" 2>&1
python ../steam_data_ETL/06_Load_Staging_To_Fact_Dim_Tables.py >> "$LOGFILE" 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') - Steam ETL pipeline completed successfully!" >> "$LOGFILE"
