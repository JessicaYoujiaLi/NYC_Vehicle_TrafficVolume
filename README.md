# NYC_Vehicle_TrafficVolume

This repository contains a Python script: nyc_vehicle.py that processes traffic volume data for New York City and visualizes it using a Dash web application. 
The application allows users to view traffic volume density on a map for different hours of the day in 2022. 
An HTML will be generated and downloaded to the directory after a selection of time is executed.

## Datasets:
download link: https://drive.google.com/file/d/16qzT1QQn9vskZFhnpVLO0L-T6QHYMROT/view?usp=drive_link
(requires lionmail)

The dataset should be named as Automated_Traffic_Volume_Counts.csv, and should be placed in the same directory as the script.

## Script Overview:

1. Load the dataset: data for the year 2022 is filtered.
2. Coordinate Transformation: The coordinates in the dataset are converted from NAD83 / New York Long Island (EPSG:2263) to WGS 84 (EPSG:4326) using the pyproj library.
3. Data Aggregation: The dataset is grouped and aggregated to calculate the average traffic volume (Vol) for each location across the year.
4. Dash App: A Dash web application is created to visualize the traffic volume density on a map.

## Runing the Script:

1. Install all the dependencies as listed in the requirement.txt, using command: pip install -r requirements.txt
2. Make sure the dataset filed is renamed, and alongside with script nyc_vehicle.py is put under the same folder.
3. Open the directory with IDE of your preference(I used VSCode), execute the script with python command in the terminal: python nyc_vehicle.py
4. The app will be available at http://127.0.0.1:8050/ by default.




