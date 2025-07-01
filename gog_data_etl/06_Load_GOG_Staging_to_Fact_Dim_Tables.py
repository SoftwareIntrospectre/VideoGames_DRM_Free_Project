import mysql.connector
import os

def load_gog_data_to_fact_and_dimensions():
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

    # Step 1: Load data into dimension tables
    # Load unique game titles
    cursor.execute("""
        INSERT INTO gog_game_title_dim (game_id, title_name, effective_date)
        SELECT DISTINCT game_id, game_title, CURDATE()
        FROM gog_games_staging
        ON DUPLICATE KEY UPDATE end_date = NULL, current_flag = TRUE
    """)

    # Load unique developers
    cursor.execute("""
        INSERT INTO gog_game_developer_dim (game_id, developer_name, effective_date)
        SELECT DISTINCT game_id, developer, CURDATE()
        FROM gog_games_staging
        ON DUPLICATE KEY UPDATE end_date = NULL, current_flag = TRUE
    """)

    # Load unique publishers
    cursor.execute("""
        INSERT INTO gog_game_publisher_dim (game_id, publisher_name, effective_date)
        SELECT DISTINCT game_id, publisher, CURDATE()
        FROM gog_games_staging
        ON DUPLICATE KEY UPDATE end_date = NULL, current_flag = TRUE
    """)

    # Load unique operating systems
    cursor.execute("""
        INSERT INTO gog_game_operating_systems_dim (game_id, operating_system_1, operating_system_2, operating_system_3, effective_date)
        SELECT game_id, operating_system_1, operating_system_2, operating_system_3, CURDATE()
        FROM gog_games_staging
        ON DUPLICATE KEY UPDATE end_date = NULL, current_flag = TRUE
    """)

    # Load unique currencies
    cursor.execute("""
        INSERT INTO gog_game_currencies_dim (price_currency)
        SELECT DISTINCT gs.price_currency
        FROM gog_games_staging gs
        ON DUPLICATE KEY UPDATE price_currency = price_currency
    """)

    # Load unique release dates
    cursor.execute("""
        INSERT INTO gog_game_release_dates_dim (game_id, store_release_date, original_release_date, effective_date)
        SELECT game_id, store_release_date, game_release_date, CURDATE()
        FROM gog_games_staging
        ON DUPLICATE KEY UPDATE end_date = NULL, current_flag = TRUE
    """)

    # Load unique product states
    cursor.execute("""
        INSERT INTO gog_game_product_state_dim (game_id, product_state, effective_date)
        SELECT game_id, product_state, CURDATE()
        FROM gog_games_staging
        ON DUPLICATE KEY UPDATE end_date = NULL, current_flag = TRUE
    """)

    # Load unique tags
    cursor.execute("""
        INSERT INTO gog_game_tags_dim (game_id, tag_1, tag_2, tag_3, tag_4, tag_5, tag_6, tag_7, tag_8, tag_9, tag_10, effective_date)
        SELECT game_id, tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8, tag9, tag10, CURDATE()
        FROM gog_games_staging
        ON DUPLICATE KEY UPDATE end_date = NULL, current_flag = TRUE
    """)

    # Step 2: Load data into the fact table
    cursor.execute("""
        INSERT INTO gog_games_fact (game_id, gog_game_title_key, gog_game_developer_key, gog_game_publisher_key, 
            gog_game_currency_key, gog_game_release_date_key, gog_game_product_state_key, 
            original_price, final_price, price            price_discount_percentage, price_discount_amount, store_url)
        SELECT 
            gs.game_id,
            (SELECT gog_game_title_key FROM gog_game_title_dim WHERE game_id = gs.game_id AND current_flag = TRUE) AS title_key,
            (SELECT gog_game_developer_key FROM gog_game_developer_dim WHERE game_id = gs.game_id AND current_flag = TRUE) AS developer_key,
            (SELECT gog_game_publisher_key FROM gog_game_publisher_dim WHERE game_id = gs.game_id AND current_flag = TRUE) AS publisher_key,
            (SELECT gog_game_currency_key FROM gog_game_currencies_dim WHERE price_currency = gs.price_currency) AS currency_key,
            (SELECT gog_game_release_date_key FROM gog_game_release_dates_dim WHERE game_id = gs.game_id AND current_flag = TRUE) AS release_date_key,
            (SELECT gog_game_product_state_key FROM gog_game_product_state_dim WHERE game_id = gs.game_id AND current_flag = TRUE) AS product_state_key,
            gs.original_price,
            gs.final_price,
            gs.price_discount_percentage,
            gs.price_discount_amount,
            gs.store_link
        FROM gog_games_staging gs
    """)

    # Commit the changes and close the connection
    db_connection.commit()
    cursor.close()
    db_connection.close()

if __name__ == '__main__':
    load_gog_data_to_fact_and_dimensions()

