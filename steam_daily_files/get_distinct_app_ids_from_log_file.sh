#!/bin/bash

'
    2024/10/24:

        This is a short-term fix to get the App IDs from the log file.
        Bug in current version that does not check for duplicates and runs too long.
        Need to do caching better to fix this. Using this for testing for now.
'

# Define the input file and output JSON file
input_file=".\steam_app_ids.log"
output_file=".\distinct_valid_app_ids.log"

# Extract distinct App IDs that are valid
distinct_ids=$(grep "App ID " "$input_file" | grep "is valid" | \
               sed -E 's/.*App ID ([0-9]+) is valid.*/\1/' | \
               sort -u | tr '\n' ',' | sed 's/,$//')

# Create JSON output
if [ -n "$distinct_ids" ]; then
    echo "{\"app_ids\": [${distinct_ids}]}" > "$output_file"
else
    echo "{\"app_ids\": []}" > "$output_file"
fi

echo "Output written to $output_file"