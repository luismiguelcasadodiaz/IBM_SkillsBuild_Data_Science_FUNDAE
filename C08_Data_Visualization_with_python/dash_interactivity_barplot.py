import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output


#read dataframe
airline_data =  pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/airline_data.csv', 
                            encoding = "ISO-8859-1",
                            dtype={'Div1Airport': str, 'Div1TailNum': str, 
                                   'Div2Airport': str, 'Div2TailNum': str})

airlines = list(airline_data['Reporting_Airline'].unique())

app = dash.Dash(__name__)

# Get the layout of the application and adjust it.
# Create an outer division using html.Div and add title to the dashboard using html.H1 component
# Add a html.Div and core input text component
# Finally, add graph component.

colors = {
    'background': '#111111',
    'text': '#0000FF'
}

app.layout = html.Div(children = [
    html.H1(children="Total number of flights to the destination state split by airline", style= {'textAlign': 'center','color':colors['text'], 'font-size': '40'}),
    html.Div(["Input Year", dcc.Input(id='input-year',type='number', value=2019, style={'height':'50px','color':colors['text'], 'font-size': '35'})], style={'color':colors['text'], 'font-size': '40'}),
    html.Div(["Airline", dcc.Dropdown(id='airline',options=airlines, value= airlines[0])]),
    html.Br(),
    html.Br(),
    html.Div([dcc.Graph(id='bar-plot')])
    ])

@app.callback(
Output(component_id = 'bar-plot', component_property = 'figure'),
Input(component_id = 'input-year', component_property = 'value'),
Input(component_id = 'airline', component_property = 'value')
)
def get_graph(entered_year, airline ):
    #Select data based on year
    df =  airline_data[ ( airline_data['Year']== entered_year ) & ( airline_data['Reporting_Airline']== airline) ]
    # Group the data by Month and compute average over arrival delay time.
    line_data = df.groupby('DestState')['Year'].count().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=line_data['DestState'], y = line_data['Year']))
    fig.update_xaxes(title_text = "Months of " + str(entered_year))
    #fig.update_yaxes(title_text = "Average arrival Delay in minutes")
    return fig

# Run the app
if __name__ == '__main__':
    app.run()