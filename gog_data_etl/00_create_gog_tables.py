import mysql.connector
import os

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

def create_tables(cursor):
    """Create tables in the database."""
    create_statements = [
        """
        CREATE TABLE IF NOT EXISTS gog_games_staging (
            stage_record_key INT AUTO_INCREMENT PRIMARY KEY,
            stage_record_loaded_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            stage_record_filename VARCHAR(255) NOT NULL,
            game_id BIGINT NOT NULL UNIQUE,
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
            tag10 VARCHAR(50)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS gog_game_title_dim (
            gog_game_title_key INT AUTO_INCREMENT PRIMARY KEY,
            game_id BIGINT NOT NULL,
            title_name VARCHAR(255) NOT NULL,
            effective_date DATE NOT NULL,
            end_date DATE,
            current_flag BOOLEAN NOT NULL DEFAULT TRUE,
            UNIQUE (game_id, effective_date)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS gog_game_developer_dim (
            gog_game_developer_key INT AUTO_INCREMENT PRIMARY KEY,
            game_id BIGINT NOT NULL,
            developer_name VARCHAR(255) NOT NULL,
            effective_date DATE NOT NULL,
            end_date DATE,
            current_flag BOOLEAN NOT NULL DEFAULT TRUE,
            UNIQUE (game_id, effective_date)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS gog_game_publisher_dim (
            gog_game_publisher_key INT AUTO_INCREMENT PRIMARY KEY,
            game_id BIGINT NOT NULL,
            publisher_name VARCHAR(255) NOT NULL,
            effective_date DATE NOT NULL,
            end_date DATE,
            current_flag BOOLEAN NOT NULL DEFAULT TRUE,
            UNIQUE (game_id, effective_date)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS gog_game_operating_systems_dim (
            gog_game_operating_system_key INT AUTO_INCREMENT PRIMARY KEY,
            game_id BIGINT NOT NULL,
            operating_system_1 VARCHAR(50),
            operating_system_2 VARCHAR(50),
            operating_system_3 VARCHAR(50),
            effective_date DATE NOT NULL,
            end_date DATE,
            current_flag BOOLEAN NOT NULL DEFAULT TRUE,
            UNIQUE (game_id, effective_date)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS gog_game_currencies_dim (
            gog_game_currency_key INT AUTO_INCREMENT PRIMARY KEY,
            price_currency VARCHAR(10) NOT NULL UNIQUE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS gog_game_release_dates_dim (
            gog_game_release_date_key INT AUTO_INCREMENT PRIMARY KEY,
            game_id BIGINT NOT NULL,
            store_release_date DATE,
            original_release_date DATE,
            effective_date DATE NOT NULL,
            end_date DATE,
            current_flag BOOLEAN NOT NULL DEFAULT TRUE,
            UNIQUE (game_id, effective_date)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS gog_game_product_state_dim (
            gog_game_product_state_key INT AUTO_INCREMENT PRIMARY KEY,
            game_id BIGINT NOT NULL,
            product_state VARCHAR(50) NOT NULL,
            effective_date DATE NOT NULL,
            end_date DATE,
            current_flag BOOLEAN NOT NULL DEFAULT TRUE,
            UNIQUE (game_id, effective_date)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS gog_game_tags_dim (
            gog_game_tag_key INT AUTO_INCREMENT PRIMARY KEY,
            game_id BIGINT NOT NULL,
            tag_1 VARCHAR(50),
            tag_2 VARCHAR(50),
            tag_3 VARCHAR(50),
            tag_4 VARCHAR(50),
            tag_5 VARCHAR(50),
            tag_6 VARCHAR(50),
            tag_7 VARCHAR(50),
            tag_8 VARCHAR(50),
            tag_9 VARCHAR(50),
            tag_10 VARCHAR(50),
            effective_date DATE NOT NULL,
            end_date DATE,
            current_flag BOOLEAN NOT NULL DEFAULT TRUE,
            UNIQUE (game_id, effective_date)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS gog_games_fact (
            gog_game_key INT AUTO_INCREMENT PRIMARY KEY,
            game_id BIGINT NOT NULL,
            gog_game_title_key INT,
            gog_game_developer_key INT,
            gog_game_publisher_key INT,
            gog_game_currency_key INT,
            gog_game_release_date_key INT,
            gog_game_product_state_key INT,
            original_price DECIMAL(10, 2),
            final_price DECIMAL(10, 2),
            price_discount_percentage DECIMAL(5, 2),
            price_discount_amount DECIMAL(10, 2),
            store_url VARCHAR(255),
            load_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (gog_game_title_key) REFERENCES gog_game_title_dim(gog_game_title_key),
            FOREIGN KEY (gog_game_developer_key) REFERENCES gog_game_developer_dim(gog_game_developer_key),
            FOREIGN KEY (gog_game_publisher_key) REFERENCES gog_game_publisher_dim(gog_game_publisher_key),
            FOREIGN KEY (gog_game_currency_key) REFERENCES gog_game_currencies_dim(gog_game_currency_key),
            FOREIGN KEY (gog_game_release_date_key) REFERENCES gog_game_release_dates_dim(gog_game_release_date_key),
            FOREIGN KEY (gog_game_product_state_key) REFERENCES gog_game_product_state_dim(gog_game_product_state_key)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS game_changes_log (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            game_id BIGINT NOT NULL,
            change_type ENUM('INSERT', 'UPDATE') NOT NULL,
            change_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY (game_id) REFERENCES gog_games_staging(game_id) ON DELETE CASCADE
        );
        """
    ]

    for statement in create_statements:
        cursor.execute(statement)
        print("Executed: ", statement.strip().splitlines()[0])  # Print the executed statement for confirmation

def main():
    """Main function to create tables in the database."""
    db_connection = connect_to_db()
    cursor = db_connection.cursor()

    try:
        create_tables(cursor)
        db_connection.commit()  # Commit the changes
        print("All tables created successfully.")
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        db_connection.rollback()  # Rollback in case of error
    finally:
        cursor.close()
        db_connection.close()

if __name__ == '__main__':
    main()
