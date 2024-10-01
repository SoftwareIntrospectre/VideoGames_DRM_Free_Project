"""
    From a single staging load, populate the Fact Table.
"""

import os
import mysql.connector

try:
    # Connect to the database
    connection = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host='localhost',
        database='drm_free_games_db'  # Your database name
    )
    
    cursor = connection.cursor()
    
    # Call the stored procedure
    cursor.callproc('Insert_From_Stage_To_Fact')

    # Fetch and print results if any
    for result in cursor.stored_results():
        for row in result.fetchall():
            print(row)

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    # Close the cursor and connection
    if cursor:
        cursor.close()
    if connection:
        connection.close()