-- Switch to the target database
USE drm_free_games_db;

-- Staging table to load data from CSV
CREATE TABLE IF NOT EXISTS gog_games_staging (
    stage_record_key INT AUTO_INCREMENT PRIMARY KEY,
    stage_record_loaded_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    stage_record_filename VARCHAR(255) NOT NULL,
    game_id BIGINT NOT NULL,  -- GOG.com ID
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

-- Dimension table for game titles
CREATE TABLE IF NOT EXISTS gog_game_title_dim (
    gog_game_title_key INT AUTO_INCREMENT PRIMARY KEY,
    title_name VARCHAR(255) NOT NULL
);

-- Dimension table for game developers
CREATE TABLE IF NOT EXISTS gog_game_developer_dim (
    gog_game_developer_key INT AUTO_INCREMENT PRIMARY KEY,
    developer_name VARCHAR(255) NOT NULL
);

-- Dimension table for publishers
CREATE TABLE IF NOT EXISTS gog_game_publisher_dim (
    gog_game_publisher_key INT AUTO_INCREMENT PRIMARY KEY,
    publisher_name VARCHAR(255) NOT NULL
);

-- Dimension table for operating systems
CREATE TABLE IF NOT EXISTS gog_game_operating_systems_dim (
    gog_game_operating_system_key INT AUTO_INCREMENT PRIMARY KEY,
    operating_system_1 VARCHAR(50),
    operating_system_2 VARCHAR(50),
    operating_system_3 VARCHAR(50)
);

-- Dimension table for currencies
CREATE TABLE IF NOT EXISTS gog_game_currencies_dim (
    gog_game_currency_key INT AUTO_INCREMENT PRIMARY KEY,
    price_currency VARCHAR(10) NOT NULL
);

-- Dimension table for release dates
CREATE TABLE IF NOT EXISTS gog_game_release_dates_dim (
    gog_game_release_date_key INT AUTO_INCREMENT PRIMARY KEY,
    store_release_date DATE,
    original_release_date DATE
);

-- Dimension table for product states
CREATE TABLE IF NOT EXISTS gog_game_product_state_dim (
    gog_game_product_state_key INT AUTO_INCREMENT PRIMARY KEY,
    product_state VARCHAR(50) NOT NULL
);

-- Dimension table for game tags
CREATE TABLE IF NOT EXISTS gog_game_tags_dim (
    gog_game_tag_key INT AUTO_INCREMENT PRIMARY KEY,
    tag_1 VARCHAR(50),
    tag_2 VARCHAR(50),
    tag_3 VARCHAR(50),
    tag_4 VARCHAR(50),
    tag_5 VARCHAR(50),
    tag_6 VARCHAR(50),
    tag_7 VARCHAR(50),
    tag_8 VARCHAR(50),
    tag_9 VARCHAR(50),
    tag_10 VARCHAR(50)
);

-- Fact table to store game details
CREATE TABLE IF NOT EXISTS gog_games_fact (
    gog_game_key INT AUTO_INCREMENT PRIMARY KEY,
    gog_game_title_key INT,
    gog_game_developer_key INT,
    gog_game_publisher_key INT,
    gog_game_operating_system_key INT,
    gog_game_currency_key INT,
    gog_game_release_date_key INT,
    gog_game_product_state_key INT,
    original_price DECIMAL(10, 2),
    final_price DECIMAL(10, 2),
    price_discount_percentage DECIMAL(5, 2),
    price_discount_amount DECIMAL(10, 2),
    store_url VARCHAR(255),
    FOREIGN KEY (gog_game_title_key) REFERENCES gog_game_title_dim(gog_game_title_key),
    FOREIGN KEY (gog_game_developer_key) REFERENCES gog_game_developer_dim(gog_game_developer_key),
    FOREIGN KEY (gog_game_publisher_key) REFERENCES gog_game_publisher_dim(gog_game_publisher_key),
    FOREIGN KEY (gog_game_operating_system_key) REFERENCES gog_game_operating_systems_dim(gog_game_operating_system_key),
    FOREIGN KEY (gog_game_currency_key) REFERENCES gog_game_currencies_dim(gog_game_currency_key),
    FOREIGN KEY (gog_game_release_date_key) REFERENCES gog_game_release_dates_dim(gog_game_release_date_key),
    FOREIGN KEY (gog_game_product_state_key) REFERENCES gog_game_product_state_dim(gog_game_product_state_key)
);

-- Association table for game tags
CREATE TABLE IF NOT EXISTS gog_game_tag_association (
    association_id INT AUTO_INCREMENT PRIMARY KEY,
    gog_game_key INT,
    gog_game_tag_key INT,
    FOREIGN KEY (gog_game_key) REFERENCES gog_games_fact(gog_game_key),
    FOREIGN KEY (gog_game_tag_key) REFERENCES gog_game_tags_dim(gog_game_tag_key)
);
