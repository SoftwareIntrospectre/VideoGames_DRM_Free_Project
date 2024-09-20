import pandas as pd
import mysql.connector
from datetime import datetime

def load_products_to_mysql(database_config, csv_filename):
    """
    Load products from a CSV file into the MySQL database.

    :param database_config: Dictionary with MySQL database connection parameters.
    :param csv_filename: Path to the CSV file containing product data.
    """
    # Connect to the MySQL database
    conn = mysql.connector.connect(**database_config)
    cursor = conn.cursor()

    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_filename, sep='|')

        # Insert records into the gog_games_staging table
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO gog_games_staging (
                    stage_record_loaded_datetime, 
                    stage_record_filename, 
                    gog_game_id, 
                    gog_game_title, 
                    gog_game_releaseDate, 
                    gog_game_storeReleaseDate, 
                    gog_game_FinalPrice, 
                    gog_game_OriginalPrice, 
                    gog_game_PriceDiscountPercentage, 
                    gog_game_PriceDiscountAmount, 
                    gog_game_PriceCurrency, 
                    gog_game_productState, 
                    gog_game_storeLink, 
                    gog_game_Developer1, 
                    gog_game_Publisher1, 
                    gog_game_OperatingSystem1, 
                    gog_game_Tag1, 
                    gog_game_Tag2, 
                    gog_game_Tag3, 
                    gog_game_Tag4, 
                    gog_game_Tag5, 
                    gog_game_Tag6, 
                    gog_game_Tag7, 
                    gog_game_Tag8, 
                    gog_game_Tag9, 
                    gog_game_Tag10, 
                    gog_game_Tag11, 
                    gog_game_Tag12, 
                    gog_game_Tag13, 
                    gog_game_Tag14, 
                    gog_game_Tag15, 
                    gog_game_Tag16, 
                    gog_game_OperatingSystem2, 
                    gog_game_OperatingSystem3, 
                    gog_game_Tag17, 
                    gog_game_Tag18
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                datetime.now(),  # Automatically add the load time
                csv_filename,
                row['id'],  # gog_game_id
                row['title'],  # gog_game_title
                row['releaseDate'],  # gog_game_releaseDate
                row['storeReleaseDate'],  # gog_game_storeReleaseDate
                row['FinalPrice'],  # gog_game_FinalPrice
                row['OriginalPrice'],  # gog_game_OriginalPrice
                row['PriceDiscountPercentage'],  # gog_game_PriceDiscountPercentage
                row['PriceDiscountAmount'],  # gog_game_PriceDiscountAmount
                row['PriceCurrency'],  # gog_game_PriceCurrency
                row['productState'],  # gog_game_productState
                row['storeLink'],  # gog_game_storeLink
                row.get('Developer1'),  # gog_game_Developer1
                row.get('Publisher1'),  # gog_game_Publisher1
                row.get('OperatingSystem1'),  # gog_game_OperatingSystem1
                row.get('Tag1'),  # gog_game_Tag1
                row.get('Tag2'),  # gog_game_Tag2
                row.get('Tag3'),  # gog_game_Tag3
                row.get('Tag4'),  # gog_game_Tag4
                row.get('Tag5'),  # gog_game_Tag5
                row.get('Tag6'),  # gog_game_Tag6
                row.get('Tag7'),  # gog_game_Tag7
                row.get('Tag8'),  # gog_game_Tag8
                row.get('Tag9'),  # gog_game_Tag9
                row.get('Tag10'),  # gog_game_Tag10
                row.get('Tag11'),  # gog_game_Tag11
                row.get('Tag12'),  # gog_game_Tag12
                row.get('Tag13'),  # gog_game_Tag13
                row.get('Tag14'),  # gog_game_Tag14
                row.get('Tag15'),  # gog_game_Tag15
                row.get('Tag16'),  # gog_game_Tag16
                row.get('OperatingSystem2'),  # gog_game_OperatingSystem2
                row.get('OperatingSystem3'),  # gog_game_OperatingSystem3
                row.get('Tag17'),  # gog_game_Tag17
                row.get('Tag18')   # gog_game_Tag18
            ))

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
    # MySQL connection configuration
    db_config = {
        'user': 'your_username',
        'password': 'your_password',
        'host': 'localhost',
        'database': 'your_database'
    }
    
    csv_filename = f"GOG_Games_List_{datetime.now().strftime('%Y%m%d')}.csv"
    load_products_to_mysql(db_config, csv_filename)
