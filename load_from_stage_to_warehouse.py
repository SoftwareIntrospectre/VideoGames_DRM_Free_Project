import os
import mysql.connector
from datetime import datetime
import load_daily_csv_to_gog_games_staging_table as stage_load
import logging

# Set up logging
logging.basicConfig(
    filename='data_load.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_and_process_data(csv_filename):
    logging.info(f'Starting data load from {csv_filename}')
    stage_load.process_csv(csv_filename)  # This is from Part 1
    logging.info('Data load completed.')

def call_stored_procedures():
    try:
        logging.info('Connecting to the database.')
        connection = mysql.connector.connect(
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            host='localhost',
            database='drm_free_games_db'  # Your database name
        )
        
        cursor = connection.cursor()
        logging.info('Database connection established.')

        # Fetch data from staging table
        cursor.execute("SELECT game_id, game_title, game_release_date, original_price, final_price, price_discount_percentage, price_discount_amount, store_link, developer, publisher, operating_system_1, operating_system_2, operating_system_3, tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8, tag9, tag10 FROM gog_games_staging;")
        
        for (game_id, title_name, game_release_date, original_price, final_price, price_discount_percentage, price_discount_amount, store_link, developer, publisher, os1, os2, os3, *tags) in cursor:
            effective_date = datetime.now().date()

            try:
                # Call stored procedures
                cursor.callproc('InsertOrUpdateGameTitle', (game_id, title_name, effective_date))
                check_unread_results(cursor)

                cursor.callproc('InsertOrUpdateGameDeveloper', (game_id, developer, effective_date))
                check_unread_results(cursor)

                cursor.callproc('InsertOrUpdateGamePublisher', (game_id, publisher, effective_date))
                check_unread_results(cursor)

                cursor.callproc('InsertOrUpdateGameReleaseDate', (game_id, game_release_date, None, effective_date))
                check_unread_results(cursor)

                cursor.callproc('InsertOrUpdateGameProductState', (game_id, 'Available', effective_date))
                check_unread_results(cursor)

                cursor.callproc('InsertOrUpdateCurrency', (store_link.split()[-1],))
                check_unread_results(cursor)

                cursor.callproc('InsertOrUpdateOperatingSystems', (game_id, os1, os2, os3, effective_date))
                check_unread_results(cursor)

                cursor.callproc('InsertOrUpdateTags', (game_id, *tags, effective_date))
                check_unread_results(cursor)

                # Insert into fact table
                cursor.callproc('InsertIntoFactTable', (game_id, original_price, final_price, price_discount_percentage, price_discount_amount, store_link, datetime.now()))
                check_unread_results(cursor)

                # Insert change log
                cursor.callproc('InsertIntoGameChangesLog', (game_id, 'INSERT', f'Inserted game with ID {game_id}'))
                check_unread_results(cursor)

                logging.info(f'Processed game with ID {game_id} successfully.')

            except mysql.connector.Error as proc_err:
                logging.error(f"Error calling stored procedures for game ID {game_id}: {proc_err}")

        connection.commit()  # Commit all changes at once
        logging.info('All changes committed successfully.')
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            logging.info('Database connection closed.')

def check_unread_results(cursor):
    """Check for unread results in the cursor. Return True if unread results are found, otherwise False."""
    try:
        for result in cursor.stored_results():
            result.fetchall()  # Consume results
        return False
    except mysql.connector.Error as err:
        logging.error(f"Unread result found: {err}")
        return True

if __name__ == '__main__':
    csv_filename = "GOG_Games_List_20240930.csv"  # You can adjust the filename as needed
    
    load_and_process_data(csv_filename)  # Execute Part 1
    call_stored_procedures()  # Execute Part 2
