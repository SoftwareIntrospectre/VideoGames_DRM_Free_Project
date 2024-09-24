import pandas as pd
import mysql.connector
from datetime import datetime
import os

def remove_carets(value):
    """Remove carets from the value if present."""
    if value and isinstance(value, str):
        return value.strip('^')
    return value

def load_products_to_mysql(database_config, csv_filename):
    # Connect to the MySQL database
    conn = mysql.connector.connect(**database_config)
    cursor = conn.cursor()

    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_filename, sep='|', engine='python', header=0)

        # Ensure that the DataFrame has the correct number of columns
        expected_columns = [
            'id', 'title', 'releaseDate', 'storeReleaseDate', 'FinalPrice',
            'OriginalPrice', 'PriceDiscountPercentage', 'PriceDiscountAmount',
            'PriceCurrency', 'productState', 'storeLink', 'Developer',
            'Publisher', 'OperatingSystem1', 'OperatingSystem2', 'OperatingSystem3', 
            'Tag1', 'Tag2', 'Tag3', 'Tag4', 'Tag5', 'Tag6', 'Tag7', 'Tag8', 'Tag9', 'Tag10'
        ]

        # Filter the DataFrame to only include the expected columns
        df = df[expected_columns]

        # Insert records into the gog_games_staging table
        for _, row in df.iterrows():
            values = (
                datetime.now(),  # Load time
                csv_filename,
                int(remove_carets(row['id'])) if pd.notna(row['id']) else None,  # game_id
                remove_carets(row['title']),  # game_title
                pd.to_datetime(remove_carets(row['releaseDate'])).date() if pd.notna(row['releaseDate']) else None,  # game_release_date
                pd.to_datetime(remove_carets(row['storeReleaseDate'])).date() if pd.notna(row['storeReleaseDate']) else None,  # store_release_date
                float(remove_carets(row['FinalPrice'])) if pd.notna(row['FinalPrice']) else None,  # final_price
                float(remove_carets(row['OriginalPrice'])) if pd.notna(row['OriginalPrice']) else None,  # original_price
                float(remove_carets(row['PriceDiscountPercentage'])) if pd.notna(row['PriceDiscountPercentage']) else None,  # price_discount_percentage
                float(remove_carets(row['PriceDiscountAmount'])) if pd.notna(row['PriceDiscountAmount']) else None,  # price_discount_amount
                remove_carets(row['PriceCurrency']),  # price_currency
                remove_carets(row['productState']),  # product_state
                remove_carets(row['storeLink']),  # store_link
                remove_carets(row['Developer']),  # developer
                remove_carets(row['Publisher']),  # publisher
                remove_carets(row['OperatingSystem1']) if pd.notna(row['OperatingSystem1']) else None,  # operating_system_1
                remove_carets(row['OperatingSystem2']) if pd.notna(row['OperatingSystem2']) else None,  # operating_system_2
                remove_carets(row['OperatingSystem3']) if pd.notna(row['OperatingSystem3']) else None,  # operating_system_3
                remove_carets(row['Tag1']) if pd.notna(row['Tag1']) else None,  # tag1
                remove_carets(row['Tag2']) if pd.notna(row['Tag2']) else None,  # tag2
                remove_carets(row['Tag3']) if pd.notna(row['Tag3']) else None,  # tag3
                remove_carets(row['Tag4']) if pd.notna(row['Tag4']) else None,  # tag4
                remove_carets(row['Tag5']) if pd.notna(row['Tag5']) else None,  # tag5
                remove_carets(row['Tag6']) if pd.notna(row['Tag6']) else None,  # tag6
                remove_carets(row['Tag7']) if pd.notna(row['Tag7']) else None,  # tag7
                remove_carets(row['Tag8']) if pd.notna(row['Tag8']) else None,  # tag8
                remove_carets(row['Tag9']) if pd.notna(row['Tag9']) else None,  # tag9
                remove_carets(row['Tag10']) if pd.notna(row['Tag10']) else None,  # tag10
            )

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
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, values)

        # Commit the changes
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()  # Roll back changes in case of error
    finally:
        # Close the connection
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # MySQL connection configuration using environment variables
    db_config = {
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'host': 'localhost',
        'database': 'drm_free_games_db'  # Your database name
    }
    
    # Specify the CSV filename
    csv_filename = f"GOG_Games_List_{datetime.now().strftime('%Y%m%d')}.csv"
    load_products_to_mysql(db_config, csv_filename)
