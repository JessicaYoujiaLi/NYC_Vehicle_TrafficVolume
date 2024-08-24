import pandas as pd
import plotly.express as px
import plotly.io as pio
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from pyproj import Transformer
from shapely import wkt

# Load the dataset
df = pd.read_csv("Automated_Traffic_Volume_Counts.csv")

# Filter for the years 2017 to 2022
df = df[df['Yr'].between(2017, 2022)]

# Define source and target CRS
source_crs = 'epsg:2263'  # NAD83 / New York Long Island
target_crs = 'epsg:4326'  # WGS 84 (latitude and longitude)

# Create a transformer object
transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)

def convert_wkt_to_lat_lon(wkt_str):
    """Convert WKT string to latitude and longitude."""
    if pd.notnull(wkt_str):  # Ensure the WKT string is not null
        try:
            point = wkt.loads(wkt_str)
            longitude, latitude = transformer.transform(point.x, point.y)
            return latitude, longitude
        except Exception as e:
            print(f"Error converting WKT: {e}")
            return None, None
    else:
        return None, None

# Apply the function to the DataFrame and create new columns
df[['Latitude', 'Longitude']] = df['WktGeom'].apply(lambda x: pd.Series(convert_wkt_to_lat_lon(x)))

# Drop any rows where conversion failed (both Latitude and Longitude are None)
df = df.dropna(subset=['Latitude', 'Longitude'])

# Group by the relevant columns
df_grouped = df.groupby(
    ['RequestID', 'Boro', 'Yr', 'M', 'D', 'HH', 'SegmentID', 'street', 'fromSt', 'toSt', 'Direction', 'Latitude', 'Longitude']
).agg({'Vol': 'sum'}).reset_index()

# Take the average value of vol for the same location across the year
df_new = df_grouped.groupby(
    ['RequestID', 'Boro', 'Yr', 'M', 'HH', 'SegmentID', 'street', 'fromSt', 'toSt','Direction', 'Latitude', 'Longitude']
).agg({'Vol': 'mean'}).reset_index()

df_aggregated = df_new.groupby(
    ['RequestID', 'Boro', 'Yr', 'HH', 'SegmentID', 'street', 'fromSt', 'toSt','Direction', 'Latitude', 'Longitude']
).agg({'Vol': 'mean'}).reset_index()

# Calculate global min and max for 'Vol'
global_min_vol = df_aggregated['Vol'].min()
global_max_vol = df_aggregated['Vol'].max()

# Create the Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(year), 'value': year} for year in sorted(df_aggregated['Yr'].unique())],
            value=df_aggregated['Yr'].min(),
            clearable=False
        ),
        dcc.Dropdown(
            id='hour-dropdown',
            options=[{'label': f'{hour}:00', 'value': hour} for hour in sorted(df_aggregated['HH'].unique())],
            value=min(df_aggregated['HH'].unique()),
            clearable=False
        )
    ]),
    dcc.Graph(id='density-map')
])

@app.callback(
    Output('density-map', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('hour-dropdown', 'value')]
)
def update_map(selected_year, selected_hour):
    filtered_df = df_aggregated[(df_aggregated['Yr'] == selected_year) & (df_aggregated['HH'] == selected_hour)]
    fig = px.scatter_mapbox(
        filtered_df,
        lat='Latitude',  # Latitude coordinates
        lon='Longitude',  # Longitude coordinates
        color='Vol',  # Use the volume as the color scale
        size='Vol',  # Set size of markers proportional to the volume
        size_max=15,  # Maximum size of the markers
        center=dict(lat=40.7128, lon=-74.0060),  # Center of the map (New York City)
        zoom=9,  # Initial zoom level of the map
        opacity=1.0,  # Set opacity to 1.0 for non-transparent colors
        color_continuous_scale=[[0, "lightgreen"], [0.25, "green"], [0.5, "yellow"], [0.75, "orange"], [1, "red"]],  # Custom green-to-yellow-to-red color scale
        range_color=(global_min_vol, global_max_vol),  # Set range for consistent color scale
        mapbox_style="carto-positron",  # Map style for the background
        hover_name='street',  # Display 'street' column on hover for more information
        hover_data={'Vol': True},  # Include relevant data on hover
        title=f'NYC Vehicle Location Density for Hour {selected_hour}:00 in {selected_year}'  # Title of the plot
    )
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=10))

    # Save the figure as HTML after it's generated
    pio.write_html(fig, file='density_map.html', auto_open=False)

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
