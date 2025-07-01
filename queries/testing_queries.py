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

    # prevents error when querying an empty table
    cursor = db_connection.cursor(buffered=True)

    # Example query to fetch all records
    # cursor.execute("SELECT * FROM gog_games_staging;")
    # cursor.execute("SELECT game_id, game_title FROM gog_games_staging;")
    # cursor.execute("select * from gog_game_developer_dim;")

    # cursor.execute("DESCRIBE steam_staging;")

    #===============================================================================#

    cursor.execute('SHOW TABLES')

    for table in [tables[0] for tables in cursor.fetchall()]:
        print(table)

    results = cursor.fetchall()

    # Get column headers
    headers = [i[0] for i in cursor.description]

    # Print headers
    print(headers)

    for row in results:
        print(row)

#===============================================================================#

    cursor.close()
    db_connection.close()

if __name__ == '__main__':
    query_database()
