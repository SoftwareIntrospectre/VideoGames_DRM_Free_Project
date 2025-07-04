import mysql.connector
import os

def query_database():
    db_config = {
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'host': 'localhost',
        'database': 'drm_free_games_db'
    }

    db_connection = mysql.connector.connect(**db_config)
    cursor = db_connection.cursor()

    # Example query to fetch all records
    cursor.execute("select * from steam_games_staging;")
    results = cursor.fetchall()

    for row in results:
        print(row)

    cursor.close()
    db_connection.close()

if __name__ == '__main__':
    query_database()
