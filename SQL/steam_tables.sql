-- Drop existing tables
DROP TABLE IF EXISTS steam_game_changes_log;
DROP TABLE IF EXISTS steam_games_staging;
DROP TABLE IF EXISTS steam_game_title_dim;
DROP TABLE IF EXISTS steam_game_developer_dim;
DROP TABLE IF EXISTS steam_game_publisher_dim;
DROP TABLE IF EXISTS steam_game_tags_dim;

-- Create Staging Table
CREATE TABLE steam_games_staging (
    steam_game_id INT PRIMARY KEY,
    steam_game_name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    developer VARCHAR(255) NOT NULL,
    publisher VARCHAR(255) NOT NULL,
    genre1_id INT NOT NULL,
    genre1_name VARCHAR(100) NOT NULL,
    release_date DATE NOT NULL,
    required_age INT NOT NULL,
    on_windows_pc_platform BOOLEAN NOT NULL,
    on_apple_mac_platform BOOLEAN NOT NULL,
    on_linux_platform BOOLEAN NOT NULL
);

-- Create Dimension Tables
CREATE TABLE steam_game_title_dim (
    steam_game_title_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    title_name VARCHAR(255) NOT NULL,
    effective_date DATE NOT NULL,
    end_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (game_id, effective_date)
);

CREATE TABLE steam_game_developer_dim (
    steam_game_developer_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    developer_name VARCHAR(255) NOT NULL,
    effective_date DATE NOT NULL,
    end_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (game_id, effective_date)
);

CREATE TABLE steam_game_publisher_dim (
    steam_game_publisher_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    publisher_name VARCHAR(255) NOT NULL,
    effective_date DATE NOT NULL,
    end_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (game_id, effective_date)
);

CREATE TABLE steam_game_tags_dim (
    steam_game_tag_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    tag_name VARCHAR(50),
    effective_date DATE NOT NULL,
    end_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (game_id, tag_name, effective_date)
);

-- Create Fact Table for Steam Games
CREATE TABLE steam_games_fact (
    steam_game_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    steam_game_title_key INT,
    steam_game_developer_key INT,
    steam_game_publisher_key INT,
    original_price DECIMAL(10, 2),
    final_price DECIMAL(10, 2),
    price_discount_percentage DECIMAL(5, 2),
    price_discount_amount DECIMAL(10, 2),
    store_url VARCHAR(255),
    load_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    composite_key VARCHAR(255),  -- Regular column now
    FOREIGN KEY (steam_game_title_key) REFERENCES steam_game_title_dim(steam_game_title_key),
    FOREIGN KEY (steam_game_developer_key) REFERENCES steam_game_developer_dim(steam_game_developer_key),
    FOREIGN KEY (steam_game_publisher_key) REFERENCES steam_game_publisher_dim(steam_game_publisher_key)
);

-- Create Trigger for Composite Key
CREATE TRIGGER after_insert_steam_games_fact
AFTER INSERT ON steam_games_fact
FOR EACH ROW
BEGIN
    DECLARE title_name VARCHAR(255);
    DECLARE developer_name VARCHAR(255);
    DECLARE publisher_name VARCHAR(255);
    DECLARE release_date DATE;

    -- Retrieve the title name from the title dimension table
    SELECT title_name INTO title_name 
    FROM steam_game_title_dim 
    WHERE steam_game_title_key = NEW.steam_game_title_key;

    -- Retrieve the developer name from the developer dimension table
    SELECT developer_name INTO developer_name 
    FROM steam_game_developer_dim 
    WHERE steam_game_developer_key = NEW.steam_game_developer_key;

    -- Retrieve the publisher name from the publisher dimension table
    SELECT publisher_name INTO publisher_name 
    FROM steam_game_publisher_dim 
    WHERE steam_game_publisher_key = NEW.steam_game_publisher_key;

    -- Retrieve the release date from the staging table
    SELECT release_date INTO release_date 
    FROM steam_games_staging 
    WHERE steam_game_id = NEW.game_id;

    -- Set the composite key using the retrieved values
    SET NEW.composite_key = CONCAT(LOWER(title_name), '|', LOWER(developer_name), '|', LOWER(publisher_name), '|', DATE_FORMAT(release_date, '%Y-%m-%d'));
END;
COMMIT;