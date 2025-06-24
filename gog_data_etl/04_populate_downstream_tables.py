import mysql.connector
import os
from datetime import datetime

# MySQL connection configuration using environment variables
db_config = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': 'localhost',
    'database': 'drm_free_games_db'
}

def connect_to_db():
    """Establish a connection to the MySQL database."""
    return mysql.connector.connect(**db_config)

def update_dimension_table(cursor, table_name, effective_date):
    print("Attempting insert into table: ", table_name)

    if table_name == 'gog_game_title_dim':
        query = f"""
        INSERT INTO {table_name} (game_id, title_name, effective_date)
        SELECT game_id, game_title, %s
        FROM gog_games_staging gs
        ON DUPLICATE KEY UPDATE
            end_date = %s,
            current_flag = FALSE;
        """
        cursor.execute(query, (effective_date, effective_date))

    elif table_name == 'gog_game_developer_dim':
        query = f"""
        INSERT INTO {table_name} (game_id, developer_name, effective_date)
        SELECT game_id, developer, %s
        FROM gog_games_staging gs
        ON DUPLICATE KEY UPDATE
            end_date = %s,
            current_flag = FALSE;
        """
        cursor.execute(query, (effective_date, effective_date))

    elif table_name == 'gog_game_publisher_dim':
        query = f"""
        INSERT INTO {table_name} (game_id, publisher_name, effective_date)
        SELECT game_id, publisher, %s
        FROM gog_games_staging gs
        ON DUPLICATE KEY UPDATE
            end_date = %s,
            current_flag = FALSE;
        """
        cursor.execute(query, (effective_date, effective_date))

    elif table_name == 'gog_game_operating_systems_dim':
        query = f"""
        INSERT INTO {table_name} (game_id, operating_system_1, operating_system_2, operating_system_3, effective_date)
        SELECT game_id, operating_system_1, operating_system_2, operating_system_3, %s
        FROM gog_games_staging gs
        ON DUPLICATE KEY UPDATE
            end_date = %s,
            current_flag = FALSE;
        """
        cursor.execute(query, (effective_date, effective_date))

    elif table_name == 'gog_game_release_dates_dim':
        query = f"""
        INSERT INTO {table_name} (game_id, store_release_date, original_release_date, effective_date)
        SELECT game_id, store_release_date, game_release_date, %s
        FROM gog_games_staging gs
        ON DUPLICATE KEY UPDATE
            end_date = %s,
            current_flag = FALSE;
        """
        cursor.execute(query, (effective_date, effective_date))

    elif table_name == 'gog_game_product_state_dim':
        query = f"""
        INSERT INTO {table_name} (game_id, product_state, effective_date)
        SELECT game_id, product_state, %s
        FROM gog_games_staging gs
        ON DUPLICATE KEY UPDATE
            end_date = %s,
            current_flag = FALSE;
        """
        cursor.execute(query, (effective_date, effective_date))

    elif table_name == 'gog_game_tags_dim':
        query = f"""
        INSERT INTO {table_name} (game_id, tag_1, tag_2, tag_3, tag_4, tag_5, tag_6, tag_7, tag_8, tag_9, tag_10, effective_date)
        SELECT game_id, tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8, tag9, tag10, %s
        FROM gog_games_staging gs
        ON DUPLICATE KEY UPDATE
            end_date = %s,
            current_flag = FALSE;
        """
        cursor.execute(query, (effective_date, effective_date))

def insert_into_fact_table(cursor):
    """Insert data into the fact table from the staging and dimension tables."""
    query = """
    INSERT INTO gog_games_fact (game_id, gog_game_title_key, gog_game_developer_key, gog_game_publisher_key, gog_game_currency_key, gog_game_release_date_key, gog_game_product_state_key, original_price, final_price, price_discount_percentage, store_url)
    SELECT gs.game_id, gtd.gog_game_title_key, gd.gog_game_developer_key, gp.gog_game_publisher_key, gc.gog_game_currency_key, gr.gog_game_release_date_key, gps.gog_game_product_state_key, 
           gs.original_price, gs.final_price, gs.price_discount_percentage, gs.store_link
    FROM gog_games_staging gs
    JOIN gog_game_title_dim gtd ON gs.game_id = gtd.game_id AND gtd.current_flag = TRUE
    JOIN gog_game_developer_dim gd ON gs.game_id = gd.game_id AND gd.current_flag = TRUE
    JOIN gog_game_publisher_dim gp ON gs.game_id = gp.game_id AND gp.current_flag = TRUE
    JOIN gog_game_currencies_dim gc ON gs.price_currency = gc.price_currency
    JOIN gog_game_release_dates_dim gr ON gs.game_id = gr.game_id AND gr.current_flag = TRUE
    JOIN gog_game_product_state_dim gps ON gs.game_id = gps.game_id AND gps.current_flag = TRUE;
    """
    cursor.execute(query)

def load_data():
    """Load data from staging to dimension and fact tables."""
    effective_date = datetime.now().date()

    # Connect to the database
    db_connection = connect_to_db()
    cursor = db_connection.cursor()

    try:
        # Update dimension tables
        update_dimension_table(cursor, 'gog_game_title_dim', effective_date)
        update_dimension_table(cursor, 'gog_game_developer_dim', effective_date)
        update_dimension_table(cursor, 'gog_game_publisher_dim', effective_date)
        update_dimension_table(cursor, 'gog_game_operating_systems_dim', effective_date)
        update_dimension_table(cursor, 'gog_game_release_dates_dim', effective_date)
        update_dimension_table(cursor, 'gog_game_product_state_dim', effective_date)
        update_dimension_table(cursor, 'gog_game_tags_dim', effective_date)

        # Insert into fact table
        insert_into_fact_table(cursor)

        # Commit the changes
        db_connection.commit()
        print("Data loaded successfully from staging to dimension and fact tables.")

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        db_connection.rollback()  # Rollback in case of error

    finally:
        cursor.close()
        db_connection.close()

if __name__ == '__main__':
    load_data()
