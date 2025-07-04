import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os

# Create a connection string for SQLAlchemy
db_config = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': '127.0.0.1',  # Ensure this is correct
    'port': '3306',        # Default MySQL port
    'database': 'drm_free_games_db'
}

# Create the SQLAlchemy engine
connection_string = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
engine = create_engine(connection_string)

# Function to fetch data from the database
def fetch_data():
    query = """
    SELECT game_title, final_price, game_release_date, developer, publisher
    FROM gog_games_staging
    """
    try:
        with engine.connect() as connection:
            df = pd.read_sql_query(query, connection)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

# Fetch data
df = fetch_data()

# Streamlit layout
st.title('GOG Games Dashboard')
st.write('A dashboard displaying GOG games with their final prices and release dates.')

# Check if the DataFrame is empty
if df.empty:
    st.write("No data fetched from the database.")
else:
    # Bar chart
    bar_fig = px.bar(
        df,
        x='game_title',
        y='final_price',
        color='developer',
        title='Final Prices of GOG Games by Developer',
        labels={'final_price': 'Final Price ($)', 'game_title': 'Game Title'},
        hover_data=['game_release_date', 'publisher']
    )
    st.plotly_chart(bar_fig)

    # Scatter plot
    scatter_fig = px.scatter(
        df,
        x='game_release_date',
        y='final_price',
        color='developer',
        title='Release Dates vs Final Prices of GOG Games',
        labels={'final_price': 'Final Price ($)', 'game_release_date': 'Release Date'},
        hover_data=['game_title', 'publisher']
    )
    st.plotly_chart(scatter_fig)
