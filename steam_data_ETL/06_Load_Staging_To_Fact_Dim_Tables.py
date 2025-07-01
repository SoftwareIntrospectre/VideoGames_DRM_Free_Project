import mysql.connector
import os

def load_data_to_fact_and_dimensions():
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
        INSERT INTO steam_game_title_dim (game_id, title_name, effective_date)
        SELECT DISTINCT steam_game_id, steam_game_name, CURDATE()
        FROM steam_staging
        ON DUPLICATE KEY UPDATE end_date = NULL, current_flag = TRUE
    """)

    # Load unique developers
    cursor.execute("""
        INSERT INTO steam_game_developer_dim (game_id, developer_name, effective_date)
        SELECT DISTINCT steam_game_id, developer_name, CURDATE()
        FROM steam_staging
        ON DUPLICATE KEY UPDATE end_date = NULL, current_flag = TRUE
    """)

    # Load unique publishers
    cursor.execute("""
        INSERT INTO steam_game_publisher_dim (game_id, publisher_name, effective_date)
        SELECT DISTINCT steam_game_id, publisher_name, CURDATE()
        FROM steam_staging
        ON DUPLICATE KEY UPDATE end_date = NULL, current_flag = TRUE
    """)

    # Load unique tags (assuming tags are stored in a single column in the staging table)
    cursor.execute("""
        INSERT INTO steam_game_tags_dim (game_id, tag_name, effective_date)
        SELECT steam_game_id, genre_1_description, CURDATE()
        FROM steam_staging
        WHERE genre_1_description IS NOT NULL
        ON DUPLICATE KEY UPDATE end_date = NULL, current_flag = TRUE
    """)

    # Step 2: Load data into the fact table
    cursor.execute("""
        INSERT INTO steam_games_fact (game_id, steam_game_title_key, steam_game_developer_key, steam_game_publisher_key, original_price, final_price, price_discount_percentage, price_discount_amount, store_url)
        SELECT 
            ss.steam_game_id,
            (SELECT steam_game_title_key FROM steam_game_title_dim WHERE game_id = ss.steam_game_id AND current_flag = TRUE) AS title_key,
            (SELECT steam_game_developer_key FROM steam_game_developer_dim WHERE game_id = ss.steam_game_id AND current_flag = TRUE) AS developer_key,
            (SELECT steam_game_publisher_key FROM steam_game_publisher_dim WHERE game_id = ss.steam_game_id AND current_flag = TRUE) AS publisher_key,
            ss.original_price,
            ss.final_price,
            ss.price_discount_percentage,
            ss.price_discount_amount,
            ss.store_url
        FROM steam_staging ss
    """)

    # Commit the changes and close the connection
    db_connection.commit()
    cursor.close()
    db_connection.close()

if __name__ == '__main__':
    load_data_to_fact_and_dimensions()
