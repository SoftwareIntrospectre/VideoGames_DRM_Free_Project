import mysql.connector
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Database connection configuration
db_config = {
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost',
    'database': 'drm_free_games_db'
}

# Function to fetch data from the database
def fetch_data(limit):
    query = f"""
    SELECT 
        s.game_title,
        COALESCE(s.developer, g.developer) AS developer,
        COALESCE(s.publisher, g.publisher) AS publisher,
        COALESCE(YEAR(s.game_release_date), YEAR(g.store_release_date)) AS release_year,
        s.final_price AS steam_price,
        g.final_price AS gog_price
    FROM 
        steam_games_fact s
    INNER JOIN 
        gog_games_fact g ON s.composite_key = g.composite_key
    ORDER BY 
        CASE WHEN g.final_price < s.final_price THEN 1 ELSE 0 END, 
        g.final_price ASC
    LIMIT {limit};
    """
    
    # Connect to the database and fetch data
    connection = mysql.connector.connect(**db_config)
    df = pd.read_sql(query, connection)
    connection.close()
    return df

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout of the dashboard
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Games Dashboard"), className="text-center")
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='game-limit',
                options=[
                    {'label': '10', 'value': 10},
                    {'label': '25', 'value': 25},
                    {'label': '50', 'value': 50},
                    {'label': '100', 'value': 100}
                ],
                value=10,
                clearable=False,
                style={'width': '50%'}
            )
        ], className="text-center")
    ]),
    dbc.Row([
        dbc.Col(dbc.Table(id='games-table'), className="mt-4")
    ])
])

# Callback to update the table based on the selected limit
@app.callback(
    Output('games-table', 'children'),
    Input('game-limit', 'value')
)
def update_table(limit):
    df = fetch_data(limit)
    if df.empty:
        return html.Tr([html.Td("No data available")])
    
    # Create table headers
    headers = [html.Thead(html.Tr([html.Th(col) for col in df.columns])))]

    # Create table rows
    rows = [html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) for i in range(len(df))]
    
    return headers + [html.Tbody(rows)]

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
