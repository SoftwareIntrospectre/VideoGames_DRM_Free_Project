import pandas as pd
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    filename=f"./steam_daily_files/steam_scraper_logger_{datetime.now().strftime('%Y%m%d')}.log", 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def save_to_csv(data, file_path):
    """
        Save the collected game details to a CSV file.

        Args:
            data (list): The game details to save.
            file_path (str): The path to the CSV file.
    """
    if not data:
        logging.warning("No data to save to CSV.")
        return

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    logging.info(f"Data saved to {file_path}.")
 
def main(data):
    """
        Main function to save data to CSV.

        Args:
            data (list): The game details to save.
    """
    csv_file_path = f"./steam_daily_files/steam_game_details_{datetime.now().strftime('%Y%m%d')}.csv"
    save_to_csv(data, csv_file_path)

# This file can be executed as a script or imported into another module.
if __name__ == "__main__":
    logging.info("Starting the data saver.")  # Log the start of the data saving process
    # Example usage:
    # main(your_data)  # Replace 'your_data' with actual data
