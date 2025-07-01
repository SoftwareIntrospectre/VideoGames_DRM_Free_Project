CREATE TABLE IF NOT EXISTS steam_games_staging (
    stage_record_key INT AUTO_INCREMENT PRIMARY KEY,
    stage_record_loaded_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    game_id BIGINT NOT NULL UNIQUE,
    game_title VARCHAR(255) NOT NULL,
    release_date DATE,
    price DECIMAL(10, 2),
    developer VARCHAR(255),
    publisher VARCHAR(255),
    tags VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS steam_game_title_dim (
    steam_game_title_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    title_name VARCHAR(255) NOT NULL,
    effective_date DATE NOT NULL,
    end_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (game_id, effective_date)
);

CREATE TABLE IF NOT EXISTS steam_game_developer_dim (
    steam_game_developer_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    developer_name VARCHAR(255) NOT NULL,
    effective_date DATE NOT NULL,
    end_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (game_id, effective_date)
);

CREATE TABLE IF NOT EXISTS steam_game_publisher_dim (
    steam_game_publisher_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    publisher_name VARCHAR(255) NOT NULL,
    effective_date DATE NOT NULL,
    end_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (game_id, effective_date)
);

CREATE TABLE IF NOT EXISTS steam_game_tags_dim (
    steam_game_tag_key INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    tag_name VARCHAR(50),
    effective_date DATE NOT NULL,
    end_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (game_id, tag_name, effective_date)
);

CREATE TABLE IF NOT EXISTS steam_games_fact (
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
    composite_key VARCHAR(255) AS (CONCAT(LOWER(game_title), '|', LOWER(developer), '|', LOWER(publisher), '|', DATE_FORMAT(game_release_date, '%Y-%m-%d'))) STORED,
    FOREIGN KEY (steam_game_title_key) REFERENCES steam_game_title_dim(steam_game_title_key),
    FOREIGN KEY (steam_game_developer_key) REFERENCES steam_game_developer_dim(steam_game_developer_key),
    FOREIGN KEY (steam_game_publisher_key) REFERENCES steam_game_publisher_dim(steam_game_publisher_key)
);

CREATE TABLE IF NOT EXISTS steam_game_changes_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    change_type ENUM('INSERT', 'UPDATE') NOT NULL,
    change_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details TEXT,
    FOREIGN KEY (game_id) REFERENCES steam_games_staging(game_id) ON DELETE CASCADE
);
