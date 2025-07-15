import csv
import mysql.connector
import os
from datetime import datetime

def process_csv(file_path):
    db_config = {
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'host': 'localhost',
        'database': 'drm_free_games_db'
    }

    db_connection = mysql.connector.connect(**db_config)
    cursor = db_connection.cursor()
    print("Database connection established.")

    # deletes from staging, if any data exists. Fresh load.
    cursor.execute("DELETE FROM steam_games_staging;")
    db_connection.commit()

    stage_record_filename = os.path.basename(file_path)

    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        headers = next(reader)

        for row in reader:
            #...re-examine this.
            if len(row) < 12:
                print(f"Skipping invalid row (not enough columns): {row}")
                continue

            try:
                release_date = datetime.strptime(row[7], "%b %d, %Y").date()
            except ValueError:
                print(f"Skipping row due to invalid date format: {row[7]}")
                continue

            cursor.execute("SELECT COUNT(*) FROM steam_games_staging WHERE steam_game_id = %s", (row[0],))
            if cursor.fetchone()[0] > 0:
                print(f"Skipping duplicate entry for game_id: {row[0]}")
                continue

            values = (
                row[0],  # steam_game_id
                row[1],  # steam_game_name
                row[2],  # price
                row[3],  # developer
                row[4],  # publisher
                row[5],  # genre1_id
                row[6],  # genre1_name
                release_date,
                row[8],  # required_age
                1 if row[9] == 'True' else 0,
                1 if row[10] == 'True' else 0,
                1 if row[11] == 'True' else 0,
            )

            try:
                print(f"Inserting values: {values}")
               
                cursor.execute("""
                    INSERT INTO steam_games_staging (
                        steam_game_id, 
                        steam_game_name,
                        price,
                        developer, 
                        publisher, 
                        genre1_id,
                        genre1_name, 
                        release_date, 
                        required_age, 
                        on_windows_pc_platform, 
                        on_apple_mac_platform, 
                        on_linux_platform
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, values)
            except mysql.connector.Error as e:
                print(f"Error inserting game_id {row[0]}: {e.msg} (Error Code: {e.errno})")

    # Commit the changes after all inserts
    db_connection.commit()
    print("All changes committed to the database.")

    # Close the cursor and connection
    cursor.close()
    db_connection.close()
    print("Database connection closed.")

if __name__ == '__main__':
    # Define the CSV filename with dynamic date
    csv_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..\\steam_daily_files', f"steam_game_details_exported_{datetime.now().strftime('%Y%m%d')}.csv")

    # Replace forward slashes with backslashes (if any)
    csv_filename = csv_filename.replace('/', '\\')
    print(f"CSV file path: {csv_filename}")

    if not os.path.isfile(csv_filename):
        print(f"File does not exist: {csv_filename}")
        exit()

    # Process the CSV file
    process_csv(csv_filename)
