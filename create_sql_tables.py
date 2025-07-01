import mysql.connector
import os
import sys

# MySQL connection configuration using environment variables
db_config = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': 'localhost',
    'database': 'drm_free_games_db'
}

def connect_to_db():
    """Establish a connection to the MySQL database."""
    return mysql.connector.connect(**db_config)

def read_sql_file(file_path):
    """Read SQL statements from a file."""
    with open(file_path, 'r') as file:
        return file.read().strip().split(';')  # Split statements by semicolon

def create_tables(cursor, sql_statements):
    """Execute a list of create table statements."""
    for statement in sql_statements:
        if statement.strip():  # Ensure the statement is not empty
            cursor.execute(statement)
            print("Executed: ", statement.strip().splitlines()[0])  # Print the executed statement for confirmation

def create_sql_tables(sql_file):
    """Create tables from the specified SQL file."""
    db_connection = connect_to_db()
    cursor = db_connection.cursor()

    try:
        sql_statements = read_sql_file(sql_file)
        create_tables(cursor, sql_statements)
        db_connection.commit()  # Commit the changes
        print(f"Tables created successfully from {sql_file}.")
    except mysql.connector.Error as e:
        print(f"Error while creating tables from {sql_file}: {e}")
        db_connection.rollback()  # Rollback in case of error
    finally:
        cursor.close()
        db_connection.close()

def main():
    """Main function to create tables in the database."""
    # create_sql_tables('sql/gog_tables.sql')
    create_sql_tables('sql/steam_tables.sql')

if __name__ == '__main__':
    main()
