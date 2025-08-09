# Import required packages
import pandas as pd
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash import  Input, Output, State, callback

# Read the airline data into pandas dataframe
airline_data =  pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/airline_data.csv', 
                            encoding = "ISO-8859-1",
                            dtype={'Div1Airport': str, 'Div1TailNum': str, 
                                   'Div2Airport': str, 'Div2TailNum': str})

# Randomly sample 500 data points. Setting the random state to be 42 so that we get same result.
data = airline_data.sample(n=500, random_state=42)

# Pie Chart Creation
fig = px.pie(data, values='Flights', names='DistanceGroup', title='Distance group proportion by flights')

# Create a dash application
app = dash.Dash(__name__)

# Get the layout of the application and adjust it.
# Create an outer division using html.Div and add title to the dashboard using html.H1 component
# Add description about the graph using HTML P (paragraph) component
# Finally, add graph component.
app.layout = html.Div(children=[html.H1("Airline On-time Performance Dashboard",
                                        style={'textAlign': 'center', 
                                                'color': '#503D36', 
                                                'font-size': 50}),
                                html.P("Proportions of distance group (250 mile distance interval group) by flights.",
                                        style={'textAlign':'center',
                                        'color': '#F57241'}),
                                dcc.Graph(figure=fig),
                                html.Button('Exit Application', id='exit-button', n_clicks=0)                                             
                                ]
                    )




@app.callback( 
    Output("status", "children"), 
    Input("exit-button", "n_clicks")
     ) 
def exit_app(n_clicks): 
    os._exit(0) # Forcefully exits the application 
    return
# Run the application                   
if __name__ == '__main__':
    app.run()