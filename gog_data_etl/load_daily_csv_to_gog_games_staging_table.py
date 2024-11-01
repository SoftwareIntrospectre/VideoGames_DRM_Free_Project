import csv
import mysql.connector
import os
import ast  # used to extract the value from a Tag's:'slug' (lowercase tag name)
from datetime import datetime

def remove_carets(value):
    return value.replace('^', '').strip()

def convert_price(value):
    return float(value) if value else None

def convert_discount(value):
    return float(value) if value else None

def convert_date(value):
    return datetime.strptime(value, '%Y-%m-%d') if value else None

def format_date(dt):
    return dt.strftime('%Y-%m-%d') if dt else None

def extract_slug_from_tag(value):
    if not value:
        return None
        # return ''
    
    try:
        # Convert the string representation of a dictionary to an actual dictionary
        data_dict = ast.literal_eval(value)
        
        # Extract the value associated with the key 'slug'
        return data_dict.get('slug')
    
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing value '{value}'; - {e}")

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
    cursor.execute("DELETE FROM gog_games_staging;")
    db_connection.commit()

    # Get the filename from the path
    stage_record_filename = os.path.basename(file_path)

    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter='|')
        headers = next(reader)  # Skip the header row
        
        for row in reader:
            # Remove carets from general values
            cleaned_columns = [remove_carets(item) for item in row]

            cleaned_row = [
                format_date(datetime.now()),  # stage_record_loaded_datetime
                stage_record_filename,  # stage_record_filename
                int(cleaned_columns[0]),  # game_id
                cleaned_columns[1],  # game_title
                format_date(convert_date(cleaned_columns[2])),  # game_release_date
                format_date(convert_date(cleaned_columns[3])),  # store_release_date
                convert_price(cleaned_columns[4]),  # final_price
                convert_price(cleaned_columns[5]),  # original_price
                convert_discount(cleaned_columns[6]),  # price_discount_percentage
                convert_price(cleaned_columns[7]),  # price_discount_amount
                cleaned_columns[8],  # price_currency
                cleaned_columns[9],  # product_state
                cleaned_columns[10],  # store_link
                cleaned_columns[11],  # developer
                cleaned_columns[12],  # publisher
                cleaned_columns[13],  # operating_system_1
                cleaned_columns[14],  # operating_system_2
                cleaned_columns[15],  # operating_system_3
                extract_slug_from_tag(cleaned_columns[16]),  # tag1
                extract_slug_from_tag(cleaned_columns[17]),  # tag2
                extract_slug_from_tag(cleaned_columns[18]),  # tag3
                extract_slug_from_tag(cleaned_columns[19]),  # tag4
                extract_slug_from_tag(cleaned_columns[20]),  # tag5
                extract_slug_from_tag(cleaned_columns[21]),  # tag6
                extract_slug_from_tag(cleaned_columns[22]),  # tag7
                extract_slug_from_tag(cleaned_columns[23]),  # tag8
                extract_slug_from_tag(cleaned_columns[24]),  # tag9
                extract_slug_from_tag(cleaned_columns[25])   # tag10
            ]

            # Check for duplicate game_id (i.e. duplicate from source API)
            cursor.execute("SELECT COUNT(*) FROM gog_games_staging WHERE game_id = %s", (cleaned_row[2],))
            if cursor.fetchone()[0] > 0:
                print(f"Skipping duplicate entry for game_id: {cleaned_row[2]}")
                continue  # Skip to the next record

            # Insert the record into the staging table
            try:
                cursor.execute("""
                    INSERT INTO gog_games_staging (
                        stage_record_loaded_datetime,
                        stage_record_filename,
                        game_id,
                        game_title,
                        game_release_date,
                        store_release_date,
                        final_price,
                        original_price,
                        price_discount_percentage,
                        price_discount_amount,
                        price_currency,
                        product_state,
                        store_link,
                        developer,
                        publisher,
                        operating_system_1,
                        operating_system_2,
                        operating_system_3,
                        tag1,
                        tag2,
                        tag3,
                        tag4,
                        tag5,
                        tag6,
                        tag7,
                        tag8,
                        tag9,
                        tag10
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, cleaned_row)
            except mysql.connector.Error as e:
                print(f"Error inserting game_id {cleaned_row[2]}: {e}")

    db_connection.commit()
    cursor.close()
    db_connection.close()

if __name__ == '__main__':
    # csv_filename = "GOG_Games_List_20240930.csv"

    # load the daily file
    csv_filename = f"./gog_daily_files/GOG_Games_List_{datetime.now().strftime('%Y%m%d')}.csv"

    process_csv(csv_filename)
