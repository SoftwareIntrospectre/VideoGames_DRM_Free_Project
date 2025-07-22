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
    # cursor.execute("select name from gog_stage LIMIT 100;")
    cursor.execute(
        f"""
        select 
          gog.game_title
        , gog.developer
        , gog.publisher
        , gog.game_release_date
        , gog.final_price
        , gog.price_discount_percentage
        , gog.original_price  
        , gog.tag1 || ', ' || gog.tag2 'genres'

        from gog_games_staging gog
        
        limit 100
        """
    )
    results = cursor.fetchall()

    for row in results:
        print(row)

    cursor.close()
    db_connection.close()

if __name__ == '__main__':
    query_database()
