/*
    Thinking through how to identify a unique game based on its data, while avoiding redundant data in each table.
*/

-- Switch to the target database
USE drm_free_games_db;

-- Staging table to load data from CSV
CREATE TABLE IF NOT EXISTS gog_games_staging (
    stage_record_key INT AUTO_INCREMENT PRIMARY KEY,
    stage_record_loaded_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    stage_record_filename VARCHAR(255) NOT NULL,
    game_id BIGINT NOT NULL UNIQUE,  -- GOG.com ID, unique for each game
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
    tags VARCHAR(255)                  -- Combined tags information
);

-- Dimension table for game titles
CREATE TABLE IF NOT EXISTS gog_game_title_dim (
    gog_game_title_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL UNIQUE,  -- Tie back to the unique game
    title_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (game_id) REFERENCES gog_games_staging(game_id) ON DELETE CASCADE
);

-- Dimension table for game developers
CREATE TABLE IF NOT EXISTS gog_game_developer_dim (
    gog_game_developer_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL UNIQUE,  -- Tie back to the unique game
    developer_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (game_id) REFERENCES gog_games_staging(game_id) ON DELETE CASCADE
);

-- Dimension table for publishers
CREATE TABLE IF NOT EXISTS gog_game_publisher_dim (
    gog_game_publisher_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL UNIQUE,  -- Tie back to the unique game
    publisher_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (game_id) REFERENCES gog_games_staging(game_id) ON DELETE CASCADE
);

-- Dimension table for currencies
CREATE TABLE IF NOT EXISTS gog_game_currency_dim (
    gog_game_currency_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL UNIQUE,  -- Tie back to the unique game
    price_currency VARCHAR(10) NOT NULL,
    FOREIGN KEY (game_id) REFERENCES gog_games_staging(game_id) ON DELETE CASCADE
);

-- Dimension table for product states
CREATE TABLE IF NOT EXISTS gog_game_product_state_dim (
    gog_game_product_state_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL UNIQUE,  -- Tie back to the unique game
    product_state VARCHAR(50) NOT NULL,
    FOREIGN KEY (game_id) REFERENCES gog_games_staging(game_id) ON DELETE CASCADE
);

-- Dimension table for operating systems
CREATE TABLE IF NOT EXISTS gog_game_operating_systems_dim (
    gog_game_operating_system_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,  -- Foreign key to reference GOG.com ID
    operating_system VARCHAR(50) NOT NULL,
    FOREIGN KEY (game_id) REFERENCES gog_games_staging(game_id) ON DELETE CASCADE,
    UNIQUE (game_id, operating_system)  -- Ensure a game doesn't have duplicate operating systems
);

-- Dimension table for game tags
CREATE TABLE IF NOT EXISTS gog_game_tags_dim (
    gog_game_tag_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,  -- Foreign key to reference GOG.com ID
    tag VARCHAR(50) NOT NULL,
    FOREIGN KEY (game_id) REFERENCES gog_games_staging(game_id) ON DELETE CASCADE,
    UNIQUE (game_id, tag)  -- Ensure a game doesn't have duplicate tags
);

-- Fact table to store game details
CREATE TABLE IF NOT EXISTS gog_games_fact (
    gog_game_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,  -- Reference to GOG's unique ID
    gog_game_title_key INT,
    gog_game_developer_key INT,
    gog_game_publisher_key INT,
    gog_game_currency_key INT,
    gog_game_product_state_key INT,
    original_price DECIMAL(10, 2),
    final_price DECIMAL(10, 2),
    price_discount_percentage DECIMAL(5, 2),
    price_discount_amount DECIMAL(10, 2),
    store_url VARCHAR(255),
    load_date DATE NOT NULL DEFAULT CURRENT_DATE,  -- To track daily loads
    FOREIGN KEY (game_id) REFERENCES gog_games_staging(game_id),
    FOREIGN KEY (gog_game_title_key) REFERENCES gog_game_title_dim(gog_game_title_key),
    FOREIGN KEY (gog_game_developer_key) REFERENCES gog_game_developer_dim(gog_game_developer_key),
    FOREIGN KEY (gog_game_publisher_key) REFERENCES gog_game_publisher_dim(gog_game_publisher_key),
    FOREIGN KEY (gog_game_currency_key) REFERENCES gog_game_currency_dim(gog_game_currency_key),
    FOREIGN KEY (gog_game_product_state_key) REFERENCES gog_game_product_state_dim(gog_game_product_state_key)
);
