import csv
import mysql.connector
import os
from datetime import datetime


def process_csv(file_path):
    # MySQL connection configuration using environment variables
    db_config = {
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'host': 'localhost',
        'database': 'drm_free_games_db'  # Your database name
    }

    # Connect to the MySQL database
    db_connection = mysql.connector.connect(**db_config)
    cursor = db_connection.cursor()

    # Clear the staging table before processing the new data
    cursor.execute("DELETE FROM steam_staging;")
    db_connection.commit() 

    # Get the filename from the path
    stage_record_filename = os.path.basename(file_path)

    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        # Use a comma as the delimiter and handle quoted strings correctly
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        headers = next(reader)  # Skip the header row
        
        for row in reader:
            # Skip rows that are empty or don't have the expected number of columns
            if len(row) < 9:  # Adjust this if your expected number of columns is different
                print(f"Skipping invalid row (not enough columns): {row}")
                continue

            # Process the date field, which is in row[7] (index 7)
            try:
                # Convert the date string to a datetime object
                release_date = datetime.strptime(row[7], "%b %d, %Y").date()
            except ValueError:
                print(f"Skipping row due to invalid date format: {row[7]}")
                continue  # Skip if date parsing fails

            # Check for duplicate game_id (i.e. duplicate from source API)
            cursor.execute("SELECT COUNT(*) FROM steam_staging WHERE steam_game_id = %s", (row[0],))
            if cursor.fetchone()[0] > 0:
                print(f"Skipping duplicate entry for game_id: {row[0]}")
                continue  # Skip to the next record

            # Prepare the values for insertion, mapping CSV fields to table fields
            values = (
                row[0],  # steam_game_id
                row[1],  # steam_game_name
                row[2],  # developer_name
                row[3],  # publisher_name
                row[5],  # genre_1_id
                row[6],  # genre_1_description
                1 if row[8] == 'True' else 0,  # on_windows_pc_platform (convert to 1/0)
                1 if row[9] == 'True' else 0,   # on_mac_platform_bool (convert to 1/0)
                1 if row[10] == 'True' else 0,  # on_linux_platform_bool (convert to 1/0)
                release_date  # release_date in YYYY-MM-DD format
            )

            # Insert the record into the staging table
            try:
                cursor.execute("""
                    INSERT INTO steam_staging (
                        steam_game_id, steam_game_name, developer_name, publisher_name, 
                        genre_1_id, genre_1_description, on_windows_pc_platform, on_mac_platform_bool,
                        on_linux_platform_bool, release_date
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, values)
            except mysql.connector.Error as e:
                print(f"Error inserting game_id {row[0]}: {e}")

    # Commit the changes and close the connection
    db_connection.commit()
    cursor.close()
    db_connection.close()


if __name__ == '__main__':
    # Define the CSV filename with dynamic date
    csv_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..\steam_daily_files', f"steam_game_details_exported_{datetime.now().strftime('%Y%m%d')}.csv")

    # Replace forward slashes with backslashes (if any)
    csv_filename = csv_filename.replace('/', '\\')
    print(csv_filename)

    if not os.path.isfile(csv_filename):
        print(f"File does not exist: {csv_filename}")
        exit  # Exit the function if the file is not found
    
    else:

        # Load the daily file
        process_csv(csv_filename)