# Project Overview

This project is intended to build a consolidated data set of which video games on Steam have an alternative on GOG.com (Good Old Games). GOG.com contains DRM-free copies (no Digital Rights Management). The intent is to extract, transform, load, and analyze data from both data sets to determine this.

The objective is to create a resource for people to observe which games on Steam have an alternative on GOG. This provides insight on an option to purchase a non-revokable license for a video game.

- **Extraction:** Python (JSON via API calls)
- **Transformation:** Python (with pandas dataframes) and SQL
- **Load:** Python and SQL (pandas and SQL Stored Procedures)

Data Modeling and Data Warehousing are also used here.

The end goal is to provide daily analytics for these combined datasets.

## Challenges So Far

1. **Determining which data to ignore**
   - For Steam games, the vast majority are invalid cases:
     1. Free games
     2. Games without release dates or that are in the future
     3. Demos, soundtracks, etc.
   
   Valid games are paid, have been released, and are classified as "games".

2. **Creating the combined data model (warehouse)**
   - GOG data is the main data, while Steam data is INNER JOINed:
     1. This is because the "business" outcome is to find all Steam games that are DRM-free, meaning they exist in GOG. That suits an INNER JOIN.
   - Maintaining this in a reasonable amount of time:
     1. Steam has over 200,000 apps on it, with a subset of those being games, and a subset of those being valid games. Even then only a subset of those will have DRM-free options.
        - I want to build this Steam dataset anyway, for analytics downstream.

## Solutions

1. Created a cache file to store processed games as they load.
2. Created a cache file to store invalid IDs (ones that are processed, but I know will never be valid cases):
   - These two create subsequent loads much faster, because I can check the JSON file saved containing ALL IDs, and essentially ignore pre-processed and invalid cases.
   - In the database, this will help focus on UPSERTs instead of truncate/reloads.
