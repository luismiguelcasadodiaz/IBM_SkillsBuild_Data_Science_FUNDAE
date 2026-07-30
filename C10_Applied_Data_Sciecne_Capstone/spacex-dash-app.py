# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
min_value=0
max_value=max_payload
Launch_sites =  spacex_df['Launch Site'].value_counts()
options=[{'label': 'All Sites', 'value': 'ALL'}]
for name in Launch_sites.index:
    options.append({'label': name, 'value': name})

  
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=options, 
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, 
                                                max=max_payload,
                                                step = 1000,
                                                marks={ i: f'{i}' for i in range(0, int(max_payload) + 1, 1000)},
                                                value=[min_value, max_value] ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                html.Br(),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class', 
        names='Launch Site', 
        title='ALL sites success rate')
        return fig
    else:
        # return the outcomes piechart for a selected site
        pre_plot_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        plot_df = pre_plot_df.groupby('class').count().reset_index()
        fig = px.pie(plot_df, values='Launch Site' ,
        names='class', 
        title=entered_site + ' success rate')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'), 
              Input(component_id="payload-slider", component_property="value"))
def get_scattar_chart(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    if entered_site == 'ALL':
        filtered_df = spacex_df[mask]
        fig = px.scatter(
            data_frame = filtered_df, 
            x ='Payload Mass (kg)', 
            y = 'class', 
            color = 'Booster Version Category', 
            title = 'Correlation between Payload and success for all sites')
        return fig
    else:
        filtered_df = spacex_df[mask & ( spacex_df['Launch Site'] == entered_site ) ]
        fig = px.scatter(
            data_frame = filtered_df, 
            x ='Payload Mass (kg)', 
            y = 'class', 
            color = 'Booster Version Category', 
            title = 'Correlation between Payload and success for site ' + entered_site)
        return fig



# Run the app
if __name__ == '__main__':
    app.run(debug=True)
