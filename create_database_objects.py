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
            sql_commands = sql_file.read().strip()
            # Split commands on the delimiter 'DELIMITER' and process each command
            commands = sql_commands.split(';')
            current_command = ""
            for command in commands:
                command = command.strip()
                if command.startswith("DELIMITER"):
                    continue  # Skip DELIMITER lines
                if command:
                    current_command += command + " "
                    if current_command.endswith("END; "):  # When we reach the end of a procedure
                        try:
                            cursor.execute(current_command[:-1])  # Remove the last space
                            proc_name = current_command.split()[2]  # Get procedure name
                            print(f"Executed command: {proc_name}")
                        except Error as err:
                            print(f"Error executing command: {current_command}\nError: {err}")
                        current_command = ""  # Reset for the next command
            connection.commit()  # Commit after all commands are executed
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()

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
            # Execute the SQL file to create stored procedures
            execute_sql_file(connection, 'create_insert_update_stored_procedures.sql')

            # Close the connection
            connection.close()
