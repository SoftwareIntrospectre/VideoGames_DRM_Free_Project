DELIMITER //

USE drm_free_games_db;

-- DROP PROCEDURE IF EXISTS InsertOrUpdateGameTitle//
-- DROP PROCEDURE IF EXISTS InsertIntoFactTable//
-- DROP PROCEDURE IF EXISTS InsertIntoGameChangesLog//
-- DROP PROCEDURE IF EXISTS InsertOrUpdateCurrency//
-- DROP PROCEDURE IF EXISTS InsertOrUpdateGameDeveloper//
-- DROP PROCEDURE IF EXISTS InsertOrUpdateGameProductState//
-- DROP PROCEDURE IF EXISTS InsertOrUpdateGamePublisher//
-- DROP PROCEDURE IF EXISTS InsertOrUpdateGameReleaseDate//
-- DROP PROCEDURE IF EXISTS InsertOrUpdateOperatingSystems//
-- DROP PROCEDURE IF EXISTS InsertOrUpdateTags//

--Create InsertOrUpdateGameTitle procedure
CREATE PROCEDURE InsertOrUpdateGameTitle()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE gameId BIGINT;
    DECLARE titleName VARCHAR(255);
    DECLARE effectiveDate DATE;

    DECLARE cur CURSOR FOR
        SELECT game_id, game_title, game_release_date
        FROM gog_games_staging;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO gameId, titleName, effectiveDate;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Check if the title already exists with the same effective date
        DECLARE currentEndDate DATE;
        SELECT end_date INTO currentEndDate
        FROM gog_game_title_dim
        WHERE game_id = gameId AND effective_date = effectiveDate;

        IF currentEndDate IS NOT NULL THEN
            -- If it exists, update the current record's end_date to today and set current_flag to FALSE
            UPDATE gog_game_title_dim
            SET end_date = CURRENT_DATE, current_flag = FALSE
            WHERE game_id = gameId AND effective_date = effectiveDate;
        END IF;

        -- Insert the new title into gog_game_title_dim
        INSERT INTO gog_game_title_dim (game_id, title_name, effective_date, current_flag)
        VALUES (gameId, titleName, effectiveDate, TRUE)
        ON DUPLICATE KEY UPDATE 
            end_date = CURRENT_DATE, current_flag = TRUE; -- Update if the key already exists
    END LOOP;

    CLOSE cur;
END //

--Create InsertOrUpdateGameDeveloper procedure
CREATE PROCEDURE InsertOrUpdateGameDeveloper(IN gameId BIGINT, IN developerName VARCHAR(255), IN effectiveDate DATE)
BEGIN
    DECLARE currentEndDate DATE;

    SELECT end_date INTO currentEndDate
    FROM gog_game_developer_dim
    WHERE game_id = gameId AND effective_date = effectiveDate;

    IF currentEndDate IS NOT NULL THEN
        UPDATE gog_game_developer_dim
        SET end_date = CURRENT_DATE, current_flag = FALSE
        WHERE game_id = gameId AND effective_date = effectiveDate;
    END IF;

    INSERT INTO gog_game_developer_dim (game_id, developer_name, effective_date, current_flag)
    VALUES (gameId, developerName, effectiveDate, TRUE);
END //

--Create InsertOrUpdateGamePublisher procedure
CREATE PROCEDURE InsertOrUpdateGamePublisher(IN gameId BIGINT, IN publisherName VARCHAR(255), IN effectiveDate DATE)
BEGIN
    DECLARE currentEndDate DATE;

    SELECT end_date INTO currentEndDate
    FROM gog_game_publisher_dim
    WHERE game_id = gameId AND effective_date = effectiveDate;

    IF currentEndDate IS NOT NULL THEN
        UPDATE gog_game_publisher_dim
        SET end_date = CURRENT_DATE, current_flag = FALSE
        WHERE game_id = gameId AND effective_date = effectiveDate;
    END IF;

    INSERT INTO gog_game_publisher_dim (game_id, publisher_name, effective_date, current_flag)
    VALUES (gameId, publisherName, effectiveDate, TRUE);
END //

--Create InsertOrUpdateGameReleaseDate procedure
CREATE PROCEDURE InsertOrUpdateGameReleaseDate(IN gameId BIGINT, IN storeReleaseDate DATE, IN originalReleaseDate DATE, IN effectiveDate DATE)
BEGIN
    DECLARE currentEndDate DATE;

    SELECT end_date INTO currentEndDate
    FROM gog_game_release_dates_dim
    WHERE game_id = gameId AND effective_date = effectiveDate;

    IF currentEndDate IS NOT NULL THEN
        UPDATE gog_game_release_dates_dim
        SET end_date = CURRENT_DATE, current_flag = FALSE
        WHERE game_id = gameId AND effective_date = effectiveDate;
    END IF;

    INSERT INTO gog_game_release_dates_dim (game_id, store_release_date, original_release_date, effective_date, current_flag)
    VALUES (gameId, storeReleaseDate, originalReleaseDate, effectiveDate, TRUE);
END //

--Create InsertOrUpdateGameProductState procedure
CREATE PROCEDURE InsertOrUpdateGameProductState(IN gameId BIGINT, IN productState VARCHAR(50), IN effectiveDate DATE)
BEGIN
    DECLARE currentEndDate DATE;

    SELECT end_date INTO currentEndDate
    FROM gog_game_product_state_dim
    WHERE game_id = gameId AND effective_date = effectiveDate;

    IF currentEndDate IS NOT NULL THEN
        UPDATE gog_game_product_state_dim
        SET end_date = CURRENT_DATE, current_flag = FALSE
        WHERE game_id = gameId AND effective_date = effectiveDate;
    END IF;

    INSERT INTO gog_game_product_state_dim (game_id, product_state, effective_date, current_flag)
    VALUES (gameId, productState, effectiveDate, TRUE);
END //

--Create InsertOrUpdateCurrency procedure
CREATE PROCEDURE InsertOrUpdateCurrency(IN priceCurrency VARCHAR(10))
BEGIN
    DECLARE currencyExists INT;

    SELECT COUNT(*) INTO currencyExists
    FROM gog_game_currencies_dim
    WHERE price_currency = priceCurrency;

    IF currencyExists = 0 THEN
        INSERT INTO gog_game_currencies_dim (price_currency)
        VALUES (priceCurrency);
    END IF;
END //

--Create InsertOrUpdateOperatingSystems procedure
CREATE PROCEDURE InsertOrUpdateOperatingSystems(IN gameId BIGINT, IN operating_system_1 VARCHAR(50), IN operating_system_2 VARCHAR(50), IN operating_system_3 VARCHAR(50), IN effectiveDate DATE)
BEGIN
    DECLARE currentEndDate DATE;

    SELECT end_date INTO currentEndDate
    FROM gog_game_operating_systems_dim
    WHERE game_id = gameId AND effective_date = effectiveDate;

    IF currentEndDate IS NOT NULL THEN
        UPDATE gog_game_operating_systems_dim
        SET end_date = CURRENT_DATE, current_flag = FALSE
        WHERE game_id = gameId AND effective_date = effectiveDate;
    END IF;

    INSERT INTO gog_game_operating_systems_dim (game_id, operating_system_1, operating_system_2, operating_system_3, effective_date, current_flag)
    VALUES (gameId, operating_system_1, operating_system_2, operating_system_3, effectiveDate, TRUE);
END //

--Create InsertOrUpdateTags procedure
CREATE PROCEDURE InsertOrUpdateTags(IN gameId BIGINT, IN tag1 VARCHAR(50), IN tag2 VARCHAR(50), IN tag3 VARCHAR(50), IN tag4 VARCHAR(50), IN tag5 VARCHAR(50),
                                     IN tag6 VARCHAR(50), IN tag7 VARCHAR(50), IN tag8 VARCHAR(50), IN tag9 VARCHAR(50), IN tag10 VARCHAR(50),
                                     IN effectiveDate DATE)
BEGIN
    DECLARE currentEndDate DATE;

    SELECT end_date INTO currentEndDate 
    FROM gog_game_tags_dim
    WHERE game_id = gameId AND effective_date = effectiveDate;

    IF currentEndDate IS NOT NULL THEN
        UPDATE gog_game_tags_dim
        SET end_date = CURRENT_DATE, current_flag = FALSE
        WHERE game_id = gameId AND effective_date = effectiveDate;
    END IF;

    INSERT INTO gog_game_tags_dim (game_id, tag_1, tag_2, tag_3, tag_4, tag_5, tag_6, tag_7, tag_8, tag_9, tag_10, effective_date, current_flag)
    VALUES (gameId, tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8, tag9, tag10, effectiveDate, TRUE);
END //

--Create InsertIntoFactTable procedure
CREATE PROCEDURE InsertIntoFactTable(
    IN gameId BIGINT,
    IN originalPrice DECIMAL(10, 2),
    IN finalPrice DECIMAL(10, 2),
    IN priceDiscountPercentage DECIMAL(5, 2),
    IN priceDiscountAmount DECIMAL(10, 2),
    IN storeUrl VARCHAR(255),
    IN loadDate DATETIME
)
BEGIN
    INSERT INTO gog_games_fact (game_id, original_price, final_price, price_discount_percentage, price_discount_amount, store_url, load_date)
    VALUES (gameId, originalPrice, finalPrice, priceDiscountPercentage, priceDiscountAmount, storeUrl, loadDate);
END //

--Create InsertIntoGameChangesLog procedure
CREATE PROCEDURE InsertIntoGameChangesLog(IN gameId BIGINT, IN changeType VARCHAR(10), IN details TEXT)
BEGIN
    IF changeType NOT IN ('INSERT', 'UPDATE') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid change type';
    END IF;

    INSERT INTO game_changes_log (game_id, change_type, change_datetime, details)
    VALUES (gameId, changeType, CURRENT_TIMESTAMP, details);
END //

COMMIT//

DELIMITER ;