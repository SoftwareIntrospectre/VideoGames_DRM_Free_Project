import subprocess
import os

# python_executable = os.getenv('DRM_FREE_GAMES_PYTHON_EXECUTABLE')
python_executable = r'C:/Users/tchac/Documents/Career/Projects\DataPlatformEngineering/VideoGames_DRM_Free_Project/venv/Scripts/python.exe'

print("Start: '01_Extract_Steam_AppIDs_To_JSON' Python script")
subprocess.run(['python', './steam_data_etl/01_Extract_Steam_AppIDs_To_JSON.py'])
print("End: '01_Extract_Steam_AppIDs_To_JSON' Python script")

print("Start: '02_Extract_Valid_Steam_AppData_To_JSON' Python script")
subprocess.run(['python', './steam_data_etl/02_Extract_Valid_Steam_AppData_To_JSON.py'])
print("End: '02_Extract_Valid_Steam_AppData_To_JSON' Python script")

print("Start: '03_Transform_Steam_App_Data_to_CSV' Python script")
subprocess.run(['python', './steam_data_etl/03_Transform_Steam_App_Data_to_CSV.py'])
print("End: '03_Transform_Steam_App_Data_to_CSV' Python script")

print("Start: '04_Load_CSV_to_Steam_Staging_Table' Python script")
subprocess.run(['python', './steam_data_etl/04_Load_CSV_to_Steam_Staging_Table.py'])
print("End: '04_Load_CSV_to_Steam_Staging_Table' Python script")

print("Start: '05_Load_CSV_to_Steam_Staging_Table' Python script")
subprocess.run(['python', './steam_data_etl/05_Load_CSV_to_Steam_Staging_Table.py'])
print("End: '05_Load_CSV_to_Steam_Staging_Table' Python script")

print("Start: '06_Load_Staging_To_Fact_Dim_Tables' Python script")
subprocess.run(['python', './steam_data_etl/06_Load_Staging_To_Fact_Dim_Tables.py'])
print("End: '06_Load_Staging_To_Fact_Dim_Tables' Python script")
