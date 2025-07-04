import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import os

# Create a connection string for SQLAlchemy
db_config = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'drm_free_games_db'
}

# Create the SQLAlchemy engine
connection_string = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
print(connection_string)

engine = create_engine(connection_string)

def fetch_data():
    query = """
    SELECT game_title, final_price, game_release_date, developer, publisher FROM gog_games_staging;
    """
    try:
        with engine.connect() as connection:
            df = pd.read_sql_query(query, connection)
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        print(f"Query: {query}")
        return pd.DataFrame()  # Return an empty DataFrame on error


# Initialize the Dash app
app = dash.Dash(__name__)

# Fetch data
df = fetch_data()

# Check if the DataFrame is empty
if df.empty:
    print("No data fetched from the database.")
else:
    # Create a simple layout
    app.layout = html.Div(children=[
        html.H1(children='GOG Games Dashboard'),

        html.Div(children=''' 
            A dashboard displaying GOG games with their final prices and release dates.
        '''),

        dcc.Graph(
            id='price-release-date-graph',
            figure=px.bar(
                df,
                x='game_title',
                y='final_price',
                color='developer',
                title='Final Prices of GOG Games by Developer',
                labels={'final_price': 'Final Price ($)', 'game_title': 'Game Title'},
                hover_data=['game_release_date', 'publisher']
            )
        ),

        dcc.Dropdown(
            id='developer-dropdown',
            options=[{'label': dev, 'value': dev} for dev in df['developer'].unique()],
            value=df['developer'].unique()[0],  # Default value
            clearable=False,
            placeholder='Select a Developer'
        ),

        dcc.Graph(
            id='release-date-graph',
            figure=px.scatter(
                df,
                x='game_release_date',
                y='final_price',
                color='developer',
                title='Release Dates vs Final Prices of GOG Games',
                labels={'final_price': 'Final Price ($)', 'game_release_date': 'Release Date'},
                hover_data=['game_title', 'publisher']
            )
        )
    ])

# Run the app
if __name__ == '__main__':
    app.run(debug=True)  # Updated line
