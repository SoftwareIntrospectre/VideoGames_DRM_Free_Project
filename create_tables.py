import mysql.connector
import os
from mysql.connector import Error

def create_connection(database_config):
    """
    Create a connection to the MySQL database.

    :param database_config: Dictionary with MySQL database connection parameters.
    :return: Connection object or None
    """
    connection = None
    try:
        connection = mysql.connector.connect(**database_config)
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def create_gog_games_staging_table(connection):
    """
    Create the gog_games_staging table in the database.

    :param connection: Connection object to the MySQL database.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS gog_games_staging (
        stage_record_key INT AUTO_INCREMENT PRIMARY KEY,
        stage_record_loaded_datetime DATETIME NOT NULL,
        stage_record_filename VARCHAR(255) NOT NULL,
        game_id INT NOT NULL,
        game_title VARCHAR(255) NOT NULL,
        game_release_date DATE,
        store_release_date DATE,
        final_price DECIMAL(10, 2),
        original_price DECIMAL(10, 2),
        price_discount_percentage DECIMAL(5, 2),
        price_discount_amount DECIMAL(10, 2),
        price_currency VARCHAR(10),
        product_state VARCHAR(50),
        store_link VARCHAR(255),
        developer VARCHAR(255),
        publisher VARCHAR(255),
        operating_system_1 VARCHAR(50),
        operating_system_2 VARCHAR(50),
        operating_system_3 VARCHAR(50),
        tag1 VARCHAR(50),
        tag2 VARCHAR(50),
        tag3 VARCHAR(50),
        tag4 VARCHAR(50),
        tag5 VARCHAR(50),
        tag6 VARCHAR(50),
        tag7 VARCHAR(50),
        tag8 VARCHAR(50),
        tag9 VARCHAR(50),
        tag10 VARCHAR(50),
        tag11 VARCHAR(50),
        tag12 VARCHAR(50),
        tag13 VARCHAR(50),
        tag14 VARCHAR(50),
        tag15 VARCHAR(50),
        tag16 VARCHAR(50),
        tag17 VARCHAR(50),
        tag18 VARCHAR(50)
    );
    """
    cursor = connection.cursor()
    try:
        cursor.execute(create_table_query)
        print("Table 'gog_games_staging' created successfully.")
    except Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()

if __name__ == "__main__":
    # MySQL connection configuration
    db_config = {
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'host': 'localhost',
        'database': 'drm_free_games_db'  # Replace with your actual database name
    }

    # Ensure that environment variables are set
    if not all(value is not None for value in [db_config['user'], db_config['password']]):
        print("Please set the MYSQL_USER and MYSQL_PASSWORD environment variables.")
    else:
        # Create a connection to the database
        connection = create_connection(db_config)

        if connection:
            # Create the table
            create_gog_games_staging_table(connection)

            # Close the connection
            connection.close()
