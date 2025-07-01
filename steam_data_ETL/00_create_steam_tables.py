import mysql.connector
import os

db_config = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': 'localhost',
    'database': 'drm_free_games_db'
}

