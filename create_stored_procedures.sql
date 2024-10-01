-- Ensure you are using the correct database
USE drm_free_games_db;  -- Change to your actual database name

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

-- Reset the delimiter back to the default
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