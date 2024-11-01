--Show counts for all tables in DB
SELECT TABLE_NAME, TABLE_ROWS
FROM information_schema.tables
WHERE table_schema = 'drm_free_games_db';

--Show available stored procedures in DB
SELECT ROUTINE_NAME
FROM information_schema.ROUTINES
WHERE ROUTINE_TYPE = 'PROCEDURE'
AND ROUTINE_SCHEMA = 'drm_free_games_db';