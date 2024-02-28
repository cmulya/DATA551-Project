from dash import dash, dash_table, callback, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import altair as alt
import os
import plotly.graph_objects as go
import plotly.express as px
import altair as alt
from datetime import date
import calendar

alt.data_transformers.disable_max_rows()

# Read in data globally
#data = pd.read_csv('../dataset/Mobi_System_Data_2023-01.csv', parse_dates=True, index_col=0)

# --------------------------------------
# STATISTICS CODE
# Number of active station:
# Path to the folder containing your files
folder_path = '../dataset'

# Initialize an empty list to store DataFrames
dfs = []

# Iterate over each file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):  # Assuming all files are CSV, you can change the condition accordingly
        file_path = os.path.join(folder_path, filename)
        # Try different encodings to read the file
        for encoding in ['utf-8', 'latin-1']:  # You can add more encodings to try if needed
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                dfs.append(df)  # Append the DataFrame to the list
                break  # Break the loop if reading is successful
            except UnicodeDecodeError:
                print(f"Error decoding file {filename} with encoding {encoding}. Trying another encoding...")

# Concatenate all DataFrames in the list into one
combined_df = pd.concat(dfs, ignore_index=True)

# Removing the bike column
combined_df = combined_df.drop(['Bike'], axis = 1)

# Remove NA values
combined_df.dropna(inplace=True)

# Convert 'Departure' to datetime
combined_df['Departure'] = pd.to_datetime(combined_df['Departure'])

# Extract month and season
combined_df['Month'] = combined_df['Departure'].dt.month
combined_df['Season'] = combined_df['Departure'].dt.month % 12 // 3 + 1

# Map season and month names
combined_df['Season'] = combined_df['Season'].map({1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'})
combined_df['Month'] = combined_df['Month'].apply(lambda x: calendar.month_abbr[x])

# Remove rows with negative duration
combined_df = combined_df[combined_df['Duration (sec.)'] >= 0]

# Data cleaning
combined_df.loc[combined_df['Departure station'].str.startswith('0099'), 'Departure station'] = "0099 šxʷƛ̓ənəq Xwtl'e7énḵ Square - Vancouver Art Gallery North Plaza"
combined_df.loc[combined_df['Return station'].str.startswith('0099'), 'Return station'] = "0099 šxʷƛ̓ənəq Xwtl'e7énḵ Square - Vancouver Art Gallery North Plaza"
combined_df.loc[combined_df['Departure station'].str.startswith('0136'), 'Departure station'] = '0136 David Lam Park - West'
combined_df.loc[combined_df['Return station'].str.startswith('0136'), 'Return station'] = '0136 David Lam Park - West'
combined_df.loc[combined_df['Departure station'].str.startswith('0201'), 'Departure station'] = '0201 Shaw Tower'
combined_df.loc[combined_df['Return station'].str.startswith('0201'), 'Return station'] = '0201 Shaw Tower'
combined_df.loc[combined_df['Departure station'].str.startswith('0237'), 'Departure station'] = '0237 Glen & 6th'
combined_df.loc[combined_df['Return station'].str.startswith('0237'), 'Return station'] = '0237 Glen & 6th'
combined_df.loc[combined_df['Departure station'].str.startswith('1002'), 'Departure station'] = '1002 PNE - Hastings & Windermere'
combined_df.loc[combined_df['Return station'].str.startswith('1002'), 'Return station'] = '1002 PNE - Hastings & Windermere'
combined_df.loc[combined_df['Departure station'].str.startswith('2143'), 'Departure station'] = '2143 War Memorial Gym'
combined_df.loc[combined_df['Return station'].str.startswith('2143'), 'Return station'] = '2143 War Memorial Gym'
combined_df.loc[combined_df['Departure station'].str.startswith('0154'), 'Departure station'] = '0155 Arbutus & McNicoll'
combined_df.loc[combined_df['Return station'].str.startswith('0154'), 'Return station'] = '0155 Arbutus & McNicoll'
combined_df.loc[combined_df['Departure station'].str.startswith('0165'), 'Departure station'] = '0150 Alexander & Main'
combined_df.loc[combined_df['Return station'].str.startswith('0165'), 'Return station'] = '0150 Alexander & Main'
values_to_remove = ['0980 Workshop - Balancer Bike Check In', '0981 Workshop - Service Complete', '0982 Workshop - Bike Testing', '0987 Quebec Yard - Rogers', '0991 HQ Workshop', '0992 Workshop - Return to Smoove', '0994 Workshop - Transmitter Testing', '0995 Workshop - Transmitter On Deck', '0997 Workshop - Demo Station', '0985 Quebec Yard - To Service', '1000 Temporary Station', '1000 Vancouver PRIDE Valet Station', '3000 Temporary Station - Celebration of Light']
combined_df = combined_df[~combined_df['Departure station'].isin(values_to_remove)]
combined_df = combined_df[~combined_df['Return station'].isin(values_to_remove)]

# Setup app and layout/frontend
app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Assistant:wght@300&display=swap",
        dbc.icons.FONT_AWESOME,
        dbc.themes.JOURNAL,
    ]
)

# Server
server = app.server

# Title
app.title = 'Bikeshare Dashboard'

# HEADER
header = html.Div(
    id="app-header",
    children=[
        html.H1(
            "Bikeshare Dashboard",
            style={
                "display": "inline",
                "font-size": "1.5em",
                "margin-left": "1.8px",
                "color": "white",  # Set font color to white
                "background-color": "#D80808",  # Set background color to red
                "padding": "10px"  # Add padding for better appearance
            }
        )
    ],
    style={"align": "center", "margin-left": 15}
)

# SIDEBAR
sidebar = dbc.Col(
    [
        header,
        html.Div(style={"height": "20px"}),
        dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard")),
                dbc.NavItem(dbc.NavLink("Trends", href="/trends")),
                dbc.NavItem(dbc.NavLink("Map", href="/map")),
            ],
            vertical=True,
            pills=True,
            className="mb-3",
        ),
    ],
    width=2.1,
    style={"background-color": "#f8f9fa", "height": "100vh", "position": "fixed", "padding-top": "20px"},
)

# TABLE FILTER
sort_table_2 = dcc.Dropdown(
    id='table_filter_1',
    options=[
        {'label': 'All', 'value': 'all'},
        {'label': '24 Hour', 'value': '24 Hour'},
        {'label': '30 Day Pass', 'value': '30 Day Pass'},
        {'label': '365 Corporate Plus', 'value': '365 Corporate Plus'},
        {'label': '365 Corporate Plus Renewal', 'value': '365 Corporate Plus Renewal'},
        {'label': '365 Corporate Standard', 'value': '365 Corporate Standard'},
        {'label': '365 Corporate Standard Renewal', 'value': '365 Corporate Standard Renewal'},
        {'label': '365 Day Founding Plus', 'value': '365 Day Founding Plus'},
        {'label': '365 Day Founding Standard', 'value': '365 Day Founding Standard'},
        {'label': '365 Day Pass Plus', 'value': '365 Day Pass Plus'},
        {'label': '365 Day Pass Plus SALE', 'value': '365 Day Pass Plus SALE'},
        {'label': '365 Day Pass Standard', 'value': '365 Day Pass Standard'},
        {'label': '365 Day Pass Standard SALE', 'value': '365 Day Pass Standard SALE'},
        {'label': 'Archived Monthly Plus', 'value': 'Archived Monthly Plus'},
        {'label': 'Archived Monthly Standard', 'value': 'Archived Monthly Standard'},
        {'label': 'Community Pass', 'value': 'Community Pass'},
        {'label': 'Community Pass E-bike', 'value': 'Community Pass E-bike'},
        {'label': 'Community Pass E-bike (PWD)', 'value': 'Community Pass E-bike (PWD)'},
        {'label': 'Herbaland Pass', 'value': 'Herbaland Pass'},
        {'label': 'Limited Classic Bikes Only (60 min)', 'value': 'Limited Classic Bikes Only (60 min)'},
        {'label': 'Pay Per Ride', 'value': 'Pay Per Ride'},
        {'label': 'UBC Inclusive Corporate Pass', 'value': 'UBC Inclusive Corporate Pass'},
        {'label': 'VIP', 'value': 'VIP'}
],
   value=['all'],
   multi=True,
   clearable=False
)

sort_table_1 = dcc.Dropdown(
    id='table_filter_2',
    options=[
        {'label': 'Electric', 'value': 'electric'},
        {'label': 'Classic', 'value': 'classic'},
        {'label': 'Both', 'value': 'both'}
   ],
   value='both',
   clearable=False
)

slider = dcc.RangeSlider(
    id='month_range_slider',
    marks={i+1: calendar.month_abbr[i+1] for i in range(12)},
    min=1,
    max=12,
    step=1,
    value=[1, 12]  # Initial range from Jan to Dec
)

# LAYOUT
app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),  # Location component to track the URL
        sidebar,
        html.Div(
            [
                html.Hr(),
                html.Div(
                    [
                        html.H6("Page / ", style={'display': 'inline'}),
                        html.H1("Average Bike Departures by Season and Month", style={"margin-bottom": "20px"}),
                        dcc.Graph(id='trend-plot1', figure={}),

                        html.H1("Average Covered Distance by Season and Month", style={"margin-bottom": "20px"}),
                        dcc.Graph(id='trend-plot2', figure={}),

                        slider
                    ],
                    className='top-bar',
                    style={'margin-bottom': '20px'}  # Add vertical space between the sidebar and top bar
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H5("Bike Type:"),
                                sort_table_1,
                                html.H5("Membershipy Type:"),
                                sort_table_2
                            ],
                            width=2,
                            style={'margin-right': '20px'}  # Add horizontal space between top bar and sort tables
                        ),
                        dbc.Col(
                            width=9
                        ),
                    ],
                    justify="center",
                    style={'margin-top': '20px'}  # Add vertical space between top bar and sort tables/map_plot
                ),
                html.Hr()
            ],
            style={"margin": "0", "margin-left": "220px", "padding-left": "20px"}  # Adjusted styles for better alignment
        ),
    ]
)

@app.callback(
    Output('trend-plot1', 'figure'),
    [Input('table_filter_2', 'value'),
     Input('table_filter_1', 'value'),
     Input('month_range_slider', 'value')]
)
def update_chart1(selected_bike, selected_membership, selected_month):

    start_month, end_month = selected_month

    selected_month_range = [int(month) for month in selected_month]
    
    # Check if 'Electric bike' is selected
    if selected_bike == 'electric':
        # Filter data for 'Electric bike'
        df = combined_df[combined_df['Electric bike'] == True]
    elif selected_bike == 'classic':
        df = combined_df[combined_df['Electric bike'] == False]
    else:
        df = combined_df

    if 'all' not in selected_membership:
        df = df[df['Membership type'].isin([m for m in selected_membership])]

    # Filter data based on selected months
    df = df[df['Month'].astype(int).between(selected_month_range[0], selected_month_range[1])]

    # Group by season, then by month, and calculate average count of bike departures
    seasonal_bike_count = df.groupby(['Season', 'Month']).size().reset_index(name='Bike Count')
    average_counts = seasonal_bike_count.groupby(['Month', 'Season'])['Bike Count'].mean().reset_index()

    # Group by season, then by month, and calculate average covered distance of bike trips
    seasonal_bike_distance = df.groupby(['Season', 'Month'])['Covered distance (m)'].mean().reset_index(name='Average Covered Distance (m)')

    # Define custom sort order for months
    month_order = ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']

    # Sort the DataFrame by the 'Month' column using the custom order
    average_counts = average_counts.loc[average_counts['Month'].isin(month_order)]
    average_counts['Month'] = pd.Categorical(average_counts['Month'], categories=month_order, ordered=True)
    average_counts = average_counts.sort_values(by='Month')

    # Sort the DataFrame by the 'Month' column using the custom order
    seasonal_bike_distance = seasonal_bike_distance.loc[seasonal_bike_distance['Month'].isin(month_order)]
    seasonal_bike_distance['Month'] = pd.Categorical(seasonal_bike_distance['Month'], categories=month_order, ordered=True)
    seasonal_bike_distance = seasonal_bike_distance.sort_values(by='Month')


    # Create separate line plots for each season
    fig_winter = px.line(
        average_counts[average_counts['Month'].isin(['Dec', 'Jan', 'Feb', 'Mar'])],
        x='Month',
        y='Bike Count',
        line_shape='linear',
        color_discrete_sequence=['blue'],
        hover_data={'Month': True, 'Bike Count': True, 'Season': True}  
    )


    fig_spring = px.line(
        average_counts[average_counts['Month'].isin(['Mar', 'Apr', 'May', 'Jun'])],
        x='Month',
        y='Bike Count',
        line_shape='linear',
        color_discrete_sequence=['green'],
        hover_data={'Month': True, 'Bike Count': True, 'Season': True}  
    )


    fig_summer = px.line(
        average_counts[average_counts['Month'].isin(['Jun', 'Jul', 'Aug', 'Sep'])],
        x='Month',
        y='Bike Count',
        line_shape='linear',
        color_discrete_sequence=['red'],
        hover_data={'Month': True, 'Bike Count': True, 'Season': True}  
    )


    fig_fall = px.line(
        average_counts[average_counts['Month'].isin(['Sep', 'Oct', 'Nov'])],
        x='Month',
        y='Bike Count',
        line_shape='linear',
        color_discrete_sequence=['yellow'],
        hover_data={'Month': True, 'Bike Count': True, 'Season': True} 
    )


    # Combine the line plots
    fig = fig_winter.add_traces(fig_spring.data)
    fig.add_traces(fig_summer.data)
    fig.add_traces(fig_fall.data)


    # Update layout
    fig.update_layout(
        yaxis_title='Average Bike Departure Count',
        xaxis = dict(
            title=None
        )
    )
    return {'data': fig['data'], 'layout': fig['layout']}

@app.callback(
    Output('trend-plot2', 'figure'),
    [Input('table_filter_2', 'value'),
     Input('table_filter_1', 'value'),
     Input('month_range_slider', 'value')]
)

def update_chart2(selected_bike, selected_membership, selected_month):

    start_month, end_month = selected_month
    
    # Check if 'Electric bike' is selected
    if selected_bike == 'electric':
        # Filter data for 'Electric bike'
        df = combined_df[combined_df['Electric bike'] == True]
    elif selected_bike == 'classic':
        df = combined_df[combined_df['Electric bike'] == False]
    else:
        df = combined_df

    if 'all' not in selected_membership:
        df = df[df['Membership type'].isin([m for m in selected_membership])]

    # Filter data based on selected months
    df = df[df['Month'].between(start_month, end_month)]

    # Group by season, then by month, and calculate average count of bike departures
    seasonal_bike_count = df.groupby(['Season', 'Month']).size().reset_index(name='Bike Count')
    average_counts = seasonal_bike_count.groupby(['Month', 'Season'])['Bike Count'].mean().reset_index()

    # Group by season, then by month, and calculate average covered distance of bike trips
    seasonal_bike_distance = df.groupby(['Season', 'Month'])['Covered distance (m)'].mean().reset_index(name='Average Covered Distance (m)')

    # Define custom sort order for months
    month_order = ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']

    # Sort the DataFrame by the 'Month' column using the custom order
    average_counts = average_counts.loc[average_counts['Month'].isin(month_order)]
    average_counts['Month'] = pd.Categorical(average_counts['Month'], categories=month_order, ordered=True)
    average_counts = average_counts.sort_values(by='Month')

    # Sort the DataFrame by the 'Month' column using the custom order
    seasonal_bike_distance = seasonal_bike_distance.loc[seasonal_bike_distance['Month'].isin(month_order)]
    seasonal_bike_distance['Month'] = pd.Categorical(seasonal_bike_distance['Month'], categories=month_order, ordered=True)
    seasonal_bike_distance = seasonal_bike_distance.sort_values(by='Month')


    # Create separate line plots for each season
    fig_winter = px.line(
        seasonal_bike_distance[seasonal_bike_distance['Month'].isin(['Dec', 'Jan', 'Feb', 'Mar'])],
        x='Month',
        y='Average Covered Distance (m)',
        line_shape='linear',
        color_discrete_sequence=['blue'],
        hover_data={'Month': True, 'Average Covered Distance (m)': True, 'Season': True}  # Add 'Season' to hover
    )

    fig_spring = px.line(
        seasonal_bike_distance[seasonal_bike_distance['Month'].isin(['Mar', 'Apr', 'May', 'Jun'])],
        x='Month',
        y='Average Covered Distance (m)',
        line_shape='linear',
        color_discrete_sequence=['green'],
        hover_data={'Month': True, 'Average Covered Distance (m)': True, 'Season': True}  # Add 'Season' to hover
    )

    fig_summer = px.line(
        seasonal_bike_distance[seasonal_bike_distance['Month'].isin(['Jun', 'Jul', 'Aug', 'Sep'])],
        x='Month',
        y='Average Covered Distance (m)',
        line_shape='linear',
        color_discrete_sequence=['red'],
        hover_data={'Month': True, 'Average Covered Distance (m)': True, 'Season': True}  # Add 'Season' to hover
    )

    fig_fall = px.line(
        seasonal_bike_distance[seasonal_bike_distance['Month'].isin(['Sep', 'Oct', 'Nov'])],
        x='Month',
        y='Average Covered Distance (m)',
        line_shape='linear',
        color_discrete_sequence=['yellow'],
        hover_data={'Month': True, 'Average Covered Distance (m)': True, 'Season': True}  # Add 'Season' to hover
    )

    # Combine the line plots
    fig = fig_winter.add_traces(fig_spring.data)
    fig.add_traces(fig_summer.data)
    fig.add_traces(fig_fall.data)

    # Update layout
    fig.update_layout(
        yaxis_title='Average Covered Distance (m)',
        xaxis = dict(
            title=None
        )
    )
    
    return {'data': fig['data'], 'layout': fig['layout']}

if __name__ == '__main__':
    app.run_server(debug=True, port=8056) 