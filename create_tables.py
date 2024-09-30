import mysql.connector
import os
from mysql.connector import Error

def create_connection(database_config):
    """
    Create a connection to the MySQL database.

    :param database_config: Dictionary with MySQL database connection parameters.
    :return: Connection object or None
    """
    connection = None
    try:
        connection = mysql.connector.connect(**database_config)
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def execute_sql_file(connection, file_path):
    """
    Execute SQL commands from a file.

    :param connection: Connection object to the MySQL database.
    :param file_path: Path to the SQL file to execute.
    """
    cursor = connection.cursor()
    try:
        with open(file_path, 'r') as sql_file:
            sql_commands = sql_file.read()
            for command in sql_commands.split(';'):
                command = command.strip()
                if command:  # Execute non-empty commands only
                    try:
                        cursor.execute(command)
                        print(f"Executed command: {command}")
                    except Error as err:
                        print(f"Error executing command: {command}\nError: {err}")
    finally:
        cursor.close()


if __name__ == "__main__":
    # MySQL connection configuration
    db_config = {
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'host': 'localhost',
        'database': 'drm_free_games_db'  # Replace with your actual database name
    }

    # Ensure that environment variables are set
    if not all(value is not None for value in [db_config['user'], db_config['password']]):
        print("Please set the MYSQL_USER and MYSQL_PASSWORD environment variables.")
    else:
        # Create a connection to the database
        connection = create_connection(db_config)

        if connection:
            # Execute the SQL file to create tables
            execute_sql_file(connection, 'create_tables.sql')

            # Close the connection
            connection.close()
