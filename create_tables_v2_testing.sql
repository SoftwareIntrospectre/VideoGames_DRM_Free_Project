/*
    1. Daily load is fetched from GOG.com's API daily
    2. Data is parsed and saved as a dataframe
    3. Dataframe is exported to CSV
    3. CSV data is read and loaded to gog_games_staging
    4. gog_games_staging is used to update fact and dimension tables.
        - Purpose is to use Slowly Changing Dimension to show changes over time, and keep track of current version of the record
*/

-- Switch to the target database
USE drm_free_games_db;

-- 1. Staging Table
CREATE TABLE IF NOT EXISTS gog_games_staging (
    stage_record_key INT AUTO_INCREMENT PRIMARY KEY,
    stage_record_loaded_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    stage_record_filename VARCHAR(255) NOT NULL,
    game_id BIGINT NOT NULL UNIQUE,  -- GOG.com ID
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

-- 2. Game Title Dimension Table
CREATE TABLE IF NOT EXISTS gog_game_title_dim (
    gog_game_title_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    title_name VARCHAR(255) NOT NULL,
    effective_date DATE NOT NULL,
    end_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (game_id, effective_date),
    FOREIGN KEY (game_id) REFERENCES gog_games_staging(game_id) ON DELETE CASCADE
);

-- 3. Game Developer Dimension Table
CREATE TABLE IF NOT EXISTS gog_game_developer_dim (
    gog_game_developer_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    developer_name VARCHAR(255) NOT NULL,
    effective_date DATE NOT NULL,
    end_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (game_id, effective_date),
    FOREIGN KEY (game_id) REFERENCES gog_games_staging(game_id) ON DELETE CASCADE
);

-- 4. Game Publisher Dimension Table
CREATE TABLE IF NOT EXISTS gog_game_publisher_dim (
    gog_game_publisher_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    publisher_name VARCHAR(255) NOT NULL,
    effective_date DATE NOT NULL,
    end_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (game_id, effective_date),
    FOREIGN KEY (game_id) REFERENCES gog_games_staging(game_id) ON DELETE CASCADE
);

-- 5. Operating Systems Dimension Table
CREATE TABLE IF NOT EXISTS gog_game_operating_systems_dim (
    gog_game_operating_system_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    operating_system_1 VARCHAR(50),
    operating_system_2 VARCHAR(50),
    operating_system_3 VARCHAR(50),
    effective_date DATE NOT NULL,
    end_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (game_id, effective_date),
    FOREIGN KEY (game_id) REFERENCES gog_games_staging(game_id) ON DELETE CASCADE
);

-- 6. Currencies Dimension Table
CREATE TABLE IF NOT EXISTS gog_game_currencies_dim (
    gog_game_currency_key INT AUTO_INCREMENT PRIMARY KEY,
    price_currency VARCHAR(10) NOT NULL UNIQUE
);

-- 7. Release Dates Dimension Table
CREATE TABLE IF NOT EXISTS gog_game_release_dates_dim (
    gog_game_release_date_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    store_release_date DATE,
    original_release_date DATE,
    effective_date DATE NOT NULL,
    end_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (game_id, effective_date),
    FOREIGN KEY (game_id) REFERENCES gog_games_staging(game_id) ON DELETE CASCADE
);

-- 8. Product States Dimension Table
CREATE TABLE IF NOT EXISTS gog_game_product_state_dim (
    gog_game_product_state_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    product_state VARCHAR(50) NOT NULL,
    effective_date DATE NOT NULL,
    end_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (game_id, effective_date),
    FOREIGN KEY (game_id) REFERENCES gog_games_staging(game_id) ON DELETE CASCADE
);

-- 9. Tags Dimension Table
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
    UNIQUE (game_id, effective_date),
    FOREIGN KEY (game_id) REFERENCES gog_games_staging(game_id) ON DELETE CASCADE
);

-- 10. Fact Table
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
    load_date DATE NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY (gog_game_title_key) REFERENCES gog_game_title_dim(gog_game_title_key),
    FOREIGN KEY (gog_game_developer_key) REFERENCES gog_game_developer_dim(gog_game_developer_key),
    FOREIGN KEY (gog_game_publisher_key) REFERENCES gog_game_publisher_dim(gog_game_publisher_key),
    FOREIGN KEY (gog_game_currency_key) REFERENCES gog_game_currencies_dim(gog_game_currency_key),
    FOREIGN KEY (gog_game_release_date_key) REFERENCES gog_game_release_dates_dim(gog_game_release_date_key),
    FOREIGN KEY (gog_game_product_state_key) REFERENCES gog_game_product_state_dim(gog_game_product_state_key)
);

-- 11. Game Changes Log Table (Optional)
CREATE TABLE IF NOT EXISTS game_changes_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    change_type ENUM('INSERT', 'UPDATE') NOT NULL,
    change_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details TEXT,
    FOREIGN KEY (game_id) REFERENCES gog_games_staging(game_id) ON DELETE CASCADE
);
