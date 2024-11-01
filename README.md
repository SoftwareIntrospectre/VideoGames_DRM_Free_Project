This project is intended to build a consolidated data set of which video games on Steam have an alternative on GOG.com (Good Old Games).
GOG.com contains DRM-free copies (no Digitial Rights Management). The intent is to extract, transform, load, and analyze data from both data sets to determine this.

Extraction: Python (JSON via API calls)
Transformation: Python (with pandas dataframes) and SQL
Load: Python and SQL (pandas and SQL Stored Procedures)

Data Modeling and Data Warehousing are also used here.

The end-goal is to provide daily analytics for these combined datasets.
