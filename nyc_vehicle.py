import pandas as pd
import plotly.express as px
import plotly.io as pio
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from pyproj import Transformer
from shapely import wkt

# Load the dataset
df = pd.read_csv("Automated_Traffic_Volume_Counts.csv")
df_2022 = df[df['Yr'] == 2022]

# Define source and target CRS
source_crs = 'epsg:2263'  # NAD83 / New York Long Island
target_crs = 'epsg:4326'  # WGS 84 (latitude and longitude)

# Create a transformer object
transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)

def convert_wkt_to_lat_lon(wkt_str):
    """Convert WKT string to latitude and longitude."""
    point = wkt.loads(wkt_str)
    longitude, latitude = transformer.transform(point.x, point.y)
    return latitude, longitude

# Apply the function to the DataFrame and create new columns
df_2022[['Latitude', 'Longitude']] = df_2022['WktGeom'].apply(lambda x: pd.Series(convert_wkt_to_lat_lon(x)))

# Group by the relevant columns and sum the 'Vol' column
df_new = df_2022.groupby(
    ['RequestID', 'Boro', 'Yr', 'M', 'D', 'HH', 'SegmentID', 'street', 'fromSt', 'toSt', 'Direction', 'Latitude', 'Longitude']
).agg({'Vol': 'sum'}).reset_index()

# Take the average value of vol for the same location across the year
df_aggregated = df_new.groupby(
    ['RequestID', 'SegmentID', 'Yr', 'M', 'HH', 'street', 'Direction', 'Latitude', 'Longitude']
).agg({'Vol': 'mean'}).reset_index()

# Calculate global min and max for 'Vol'
global_min_vol = df_aggregated['Vol'].min()
global_max_vol = df_aggregated['Vol'].max()

# Create the Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='hour-dropdown',
            options=[{'label': f'{hour}:00', 'value': hour} for hour in df_aggregated['HH'].unique()],
            value=df_aggregated['HH'].min(),
            clearable=False
        )
    ]),
    dcc.Graph(id='density-map')
])

@app.callback(
    Output('density-map', 'figure'),
    [Input('hour-dropdown', 'value')]
)
def update_map(selected_hour):
    filtered_df = df_aggregated[df_aggregated['HH'] == selected_hour]
    fig = px.density_mapbox(
        filtered_df,
        lat='Latitude',  # Latitude coordinates
        lon='Longitude',  # Longitude coordinates
        z='Vol',  # Use the aggregated volume as the intensity
        radius=20,  # Increased radius to make points more visible
        center=dict(lat=40.7128, lon=-74.0060),  # Center of the map (New York City)
        zoom=9,  # Initial zoom level of the map
        opacity=0.9,  # Set minimum opacity to make points less transparent
        color_continuous_scale=[[0, "lightgreen"], [0.25, "green"],[0.5, "yellow"],[0.75, "orange"],[1, "red"]],  # Custom green-to-yellow-to-red color scale
        range_color=(global_min_vol, global_max_vol),  # Set range for consistent color scale
        mapbox_style="carto-positron",  # Map style for the background
        hover_name='street',  # Display 'street' column on hover for more information
        hover_data={'RequestID': True, 'Vol': True, 'Yr': True,'M': True },  # Include additional hover data
        title=f'NYC Vehicle Location Density for Hour {selected_hour}:00 in 2022'  # Title of the plot
    )
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=10))

    # Save the figure as HTML after it's generated
    pio.write_html(fig, file='density_map.html', auto_open=False)

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
