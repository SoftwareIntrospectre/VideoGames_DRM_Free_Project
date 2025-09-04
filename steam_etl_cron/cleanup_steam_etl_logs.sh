# removes logs older than 1 week
find . -name "steam_etl_*.log" -type f -mtime +7 -exec rm {} \;
