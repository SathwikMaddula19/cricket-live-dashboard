import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
pg_password = os.getenv("POSTGRES_PASSWORD")


def get_data():
    """Pull the latest match data from PostgreSQL into a pandas DataFrame."""
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="cricket_dashboard",
        user="postgres",
        password=pg_password
    )
    df = pd.read_sql("SELECT * FROM live_matches ORDER BY last_updated DESC;", conn)
    conn.close()
    return df


app = dash.Dash(__name__)
app.title = "Cricket Live Dashboard"

app.layout = html.Div([
    html.H1("Live Cricket Match Dashboard"),

    html.Div(id="last-refresh-text"),

    dcc.Interval(
        id="interval-component",
        interval=30 * 1000,  # refresh every 30 seconds (in milliseconds)
        n_intervals=0
    ),

    dcc.Graph(id="matches-by-venue-chart"),

    html.H3("Live Match Table"),
    dash_table.DataTable(
        id="matches-table",
        columns=[
            {"name": "Match", "id": "match_name"},
            {"name": "Type", "id": "match_type"},
            {"name": "Status", "id": "status"},
            {"name": "Venue", "id": "venue"},
            {"name": "Date", "id": "match_date"},
        ],
        page_size=10,
        style_cell={"textAlign": "left"},
    ),
])


@app.callback(
    [Output("matches-by-venue-chart", "figure"),
     Output("matches-table", "data"),
     Output("last-refresh-text", "children")],
    [Input("interval-component", "n_intervals")]
)
def update_dashboard(n):
    df = get_data()

    if df.empty:
        fig = px.bar(title="No data yet")
        return fig, [], "No data available yet."

    venue_counts = df["venue"].value_counts().reset_index()
    venue_counts.columns = ["venue", "match_count"]

    fig = px.bar(
        venue_counts,
        x="venue",
        y="match_count",
        title="Matches by Venue"
    )

    last_updated = df["last_updated"].max()
    refresh_text = f"Last data refresh: {last_updated}"

    return fig, df.to_dict("records"), refresh_text


if __name__ == "__main__":
    app.run(debug=True)
