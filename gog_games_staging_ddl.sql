--DDLs
CREATE TABLE gog_games_load_tracker (
    load_number INTEGER PRIMARY KEY AUTOINCREMENT
);

CREATE TABLE gog_games_staging AS
(
	gog_game_stage_record_key INTEGER PRIMARY KEY AUTOINCREMENT,
    stage_record_loaded_datetime DATETIME,
    stage_record_filename VARCHAR(500),
	gog_game_id VARCHAR(500),
	gog_game_title VARCHAR(500),
	gog_game_releaseDate VARCHAR(500),
	gog_game_storeReleaseDate VARCHAR(500),
	gog_game_FinalPrice VARCHAR(500),
	gog_game_OriginalPrice VARCHAR(500),
	gog_game_PriceDiscountPercentage VARCHAR(500),
	gog_game_PriceDiscountAmount VARCHAR(500),
	gog_game_PriceCurrency VARCHAR(500),
	gog_game_productState VARCHAR(500),
	gog_game_storeLink VARCHAR(500),
	gog_game_Developer1 VARCHAR(500),
	gog_game_Publisher1 VARCHAR(500),
	gog_game_OperatingSystem1 VARCHAR(500),
	gog_game_Tag1 VARCHAR(500),
	gog_game_Tag2 VARCHAR(500),
	gog_game_Tag3 VARCHAR(500),
	gog_game_Tag4 VARCHAR(500),
	gog_game_Tag5 VARCHAR(500),
	gog_game_Tag6 VARCHAR(500),
	gog_game_Tag7 VARCHAR(500),
	gog_game_Tag8 VARCHAR(500),
	gog_game_Tag9 VARCHAR(500),
	gog_game_Tag10 VARCHAR(500),
	gog_game_Tag11 VARCHAR(500),
	gog_game_Tag12 VARCHAR(500),
	gog_game_Tag13 VARCHAR(500),
	gog_game_Tag14 VARCHAR(500),
	gog_game_Tag15 VARCHAR(500),
	gog_game_Tag16 VARCHAR(500),
	gog_game_OperatingSystem2 VARCHAR(500),
	gog_game_OperatingSystem3 VARCHAR(500),
	gog_game_Tag17 VARCHAR(500),
	gog_game_Tag18 VARCHAR(500)
);

--DML: auto-increment the load number, and keep track of it per-load
INSERT INTO gog_games_load_tracker DEFAULT VALUES;

SELECT MAX(load_number) FROM load_tracker;

INSERT INTO products (stage_record_loaded_datetime, stage_record_filename, stage_load_number, id, title, ...)
VALUES (datetime('now'), 'myfile.csv', (SELECT MAX(load_number) FROM load_tracker), '123', 'My Product', ...);
