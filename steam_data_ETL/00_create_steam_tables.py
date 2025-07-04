import mysql.connector
import os

db_config = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': 'localhost',
    'database': 'drm_free_games_db'
}

def connect_to_db():
    """Establish a connection to the MySQL database."""
    return mysql.connector.connect(**db_config)

def create_tables_from_file(cursor, file_path):
    """Create tables in the database from the provided SQL file."""
    with open(file_path, 'r') as sql_file:
        sql_script = sql_file.read()
    
    # Split the script into individual statements
    statements = sql_script.split(';')
    
    current_statement = ""
    
    for statement in statements:
        statement = statement.strip()
        
        # Skip comments and empty statements
        if not statement or statement.startswith('--'):
            continue
        
        # Accumulate multi-line statements
        current_statement += statement + " "
        
        # If the statement ends with a semicolon, execute it
        if statement.endswith('END') or statement.endswith(';'):
            try:
                # Execute the accumulated statement
                cursor.execute(current_statement.strip())
                print("Executed: ", current_statement.strip())  # Print the executed statement for confirmation
            except mysql.connector.Error as e:
                print(f"Error executing statement: {current_statement.strip()}")
                print(f"Error: {e}")
            finally:
                current_statement = ""  # Reset for the next statement

    # If there's any remaining statement that hasn't been executed
    if current_statement.strip():
        try:
            cursor.execute(current_statement.strip())
            print("Executed: ", current_statement.strip())
        except mysql.connector.Error as e:
            print(f"Error executing statement: {current_statement.strip()}")
            print(f"Error: {e}")


def main():
    """Main function to create tables in the database."""
    db_connection = connect_to_db()
    cursor = db_connection.cursor()

    try:
        # Specify the path to the SQL file
        sql_file_path = os.path.join(os.path.dirname(__file__), '../SQL/steam_tables.sql')
        create_tables_from_file(cursor, sql_file_path)
        db_connection.commit()  # Commit the changes
        print("All tables created successfully.")

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        db_connection.rollback()

    finally:
        cursor.close()
        db_connection.close()

if __name__ == '__main__':
    main()
