USE drm_free_games_db;

-- Set the delimiter to handle the procedure definition
DELIMITER //

-- Drop the procedure if it already exists
DROP PROCEDURE IF EXISTS Insert_From_Stage_To_Game_Title_Dim;

-- Create or replace the procedure
CREATE OR REPLACE PROCEDURE Insert_From_Stage_To_Game_Title_Dim()
BEGIN
    -- IGNORE does not insert duplicate records
    INSERT IGNORE INTO gog_game_title_dim (title_name)
    SELECT game_title FROM gog_games_staging;
END //

DELIMITER ;


-- DELIMITER //

-- CREATE OR REPLACE PROCEDURE Insert_From_Stage_To_Fact()
-- BEGIN
--     INSERT INTO gog_games_fact (
--           gog_game_title_key            
--         , original_price                
--         , final_price                   
--         , price_discount_percentage     
--         , price_discount_amount         
--         , store_url                     
--     )
--     SELECT 
--           game_id            
--         , original_price                
--         , final_price                   
--         , price_discount_percentage     
--         , price_discount_amount         
--         , store_link

--     FROM gog_games_staging;
-- END //

DELIMITER //

-- Drop the procedure if it already exists
DROP PROCEDURE IF EXISTS Insert_From_Stage_To_Game_Developer_Dim;

-- Create or replace the procedure
CREATE OR REPLACE PROCEDURE Insert_From_Stage_To_Game_Developer_Dim()
BEGIN
    -- IGNORE does not insert duplicate records
    INSERT IGNORE INTO gog_game_developer_dim(developer_name)
    SELECT developer FROM gog_games_staging;
END //

DELIMITER ;




DELIMITER //

-- Drop the procedure if it already exists
DROP PROCEDURE IF EXISTS Insert_From_Stage_To_Game_Developer_Dim;

-- Create or replace the procedure
CREATE OR REPLACE PROCEDURE Insert_From_Stage_To_Game_Publisher_Dim()
BEGIN
    -- IGNORE does not insert duplicate records
    INSERT IGNORE INTO gog_game_publisher_dim(publisher_name)
    SELECT publisher FROM gog_games_staging;
END //

DELIMITER ;



DELIMITER //

-- Drop the procedure if it already exists
DROP PROCEDURE IF EXISTS Insert_From_Stage_To_Game_Operating_Systems_Dim;

-- Create or replace the procedure
CREATE OR REPLACE PROCEDURE Insert_From_Stage_To_Game_Publisher_Dim()
BEGIN
    -- IGNORE does not insert duplicate records
    INSERT IGNORE INTO gog_game_operating_systems_dim(operating_system_1, operating_system_2, operating_system_3)
    SELECT operating_system_1, operating_system_2, operating_system_3 FROM gog_games_staging;
END //

DELIMITER ;
