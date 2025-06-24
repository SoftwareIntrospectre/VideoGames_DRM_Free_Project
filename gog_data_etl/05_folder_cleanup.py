import os
import zipfile
from datetime import datetime, timedelta

# Directory to manage
DIRECTORY = "./gog_daily_files"

def compress_old_csvs():
    """Compress all CSV files older than a week into a zip archive and delete the originals."""
    now = datetime.now()
    week_ago = now - timedelta(weeks=1)
    seventy_two_hours_ago = now - timedelta(hours=72)
    csv_files = [f for f in os.listdir(DIRECTORY) if f.endswith('.csv')]
    
    if csv_files:
        # Create a zip file with the current date
        zip_filename = os.path.join(DIRECTORY, f"csv_archive_{now.strftime('%Y-%m-%d')}.zip")
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for csv_file in csv_files:
                file_path = os.path.join(DIRECTORY, csv_file)
                file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                # Check if the file is older than a week and not within the last 72 hours
                if file_mod_time < week_ago and file_mod_time < seventy_two_hours_ago:
                    zipf.write(file_path, arcname=csv_file)
                    print(f"Compressed: {csv_file} into {zip_filename}")
                    # Delete the original CSV file after archiving
                    os.remove(file_path)
                    print(f"Deleted original CSV file: {csv_file}")

def delete_old_zips():
    """Delete zip files older than one month."""
    now = datetime.now()
    month_ago = now - timedelta(days=30)
    zip_files = [f for f in os.listdir(DIRECTORY) if f.endswith('.zip')]
    
    for zip_file in zip_files:
        file_path = os.path.join(DIRECTORY, zip_file)
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        if file_mod_time < month_ago:
            os.remove(file_path)
            print(f"Deleted old zip file: {zip_file}")

def main():
    compress_old_csvs()
    delete_old_zips()

if __name__ == "__main__":
    main()
