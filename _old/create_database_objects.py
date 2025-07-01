import mysql.connector
import os
from mysql.connector import Error

def create_connection(database_config):
    """
    Create a connection to the MySQL database.
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
    """
    cursor = connection.cursor()
    try:
        with open(file_path, 'r') as sql_file:
            sql_commands = sql_file.read().strip()
            # Split the commands by 'DELIMITER' and manage procedure definitions
            commands = sql_commands.split('DELIMITER')
            current_command = ""
            current_delimiter = ";"

            for i, part in enumerate(commands):
                part = part.strip()
                if i == 0:
                    # This part does not change the delimiter
                    current_command += part + " "
                else:
                    # Handle the commands split by the new delimiter
                    new_delim = part.split()[0]
                    command_body = part[len(new_delim):].strip()
                    
                    if command_body.endswith("END"):
                        current_command += command_body
                        # Execute the full command
                        try:
                            cursor.execute(current_command)
                            proc_name = current_command.split()[2]  # Get procedure name
                            print(f"Executed command: {proc_name}")
                        except Error as err:
                            print(f"Error executing command: {current_command}\nError: {err}")
                        current_command = ""  # Reset for the next command
                    else:
                        current_command += part + " "
                    # Update the current delimiter
                    current_delimiter = new_delim

            connection.commit()  # Commit after all commands are executed
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
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
            # Execute the SQL file to create stored procedures
            execute_sql_file(connection, 'create_insert_update_stored_procedures.sql')

            # Close the connection
            connection.close()
