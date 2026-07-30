

import dash
import pandas as pd
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update
import datetime as dt

#Create app

app = dash.Dash(__name__)

# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

# Read the wildfire data into pandas dataframe
df =  pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/Historical_Wildfires.csv')

#Extract year and month from the date column

df['Month'] = pd.to_datetime(df['Date']).dt.month_name() #used for the names of the months
df['Month_num'] = pd.to_datetime(df['Date']).dt.month #used for the numbers of the months
df['Year'] = pd.to_datetime(df['Date']).dt.year
regions = [ { "label" : "New South Wales"    , "value" : "NSW" },
            { "label" : "Northern Territory" , "value" : "NT"  },
            { "label" : "Queensland"         , "value" : "QL"  },
            { "label" : "South Australia"    , "value" : "SA"  },
            { "label" : "Tasmania"           , "value" : "TA"  },
            { "label" : "Victoria"           , "value" : "VI"  },
            { "label" : "Western Australia"  , "value" : "WA"  } ]
years = df['Year'].unique()
default_year = years[0]

#Layout Section of Dash

#Task 2.1 Add the Title to the Dashboard
app.layout = html.Div(children=[html.H1(children='Australia Wildfire Dashboard',
                                        style = { 'textAlign' : 'center' ,
                                                  'color'     : '#503D36' ,
                                                  'font-size' : 26 }
                                       ),

# TASK 2.2: Add the radio items and a dropdown right below the first inner division
#outer division starts
     html.Div([
                   # First inner divsion for  adding dropdown helper text for Selected Drive wheels
                    html.Div([
                                html.H2(children='Select Region:',
                                        style = { 'margin-right' : '2em' }
                                        ),

                                #Radio items to select the region
                                #dcc.RadioItems(['NSW',.....], value ='...', id='...',inline=True)]),
                                dcc.RadioItems( options = regions, 
                                                value = "NSW",
                                                id='region',
                                                inline=True)
                            ]),
                    #Dropdown to select year
                    html.Div([
                                html.H2(children='Select Year:',
                                        style={ 'margin-right' : '2em' }
                                        ),
                                dcc.Dropdown(options = years,
                                             value = default_year,
                                             id='the-year')
                            ]),
#Second Inner division for adding 2 inner divisions for 2 output graphs
#TASK 2.3: Add two empty divisions for output inside the next inner division.
                    html.Div([
                
                                html.Div([dcc.Graph(id='plot1')]),
                                html.Div([dcc.Graph(id='plot2')])
                            ], 
                            style={'display': 'flex','margin-right' : '2em'}
                            ),

    ])
    #outer division ends

])
#layout ends
#TASK 2.4: Add the Ouput and input components inside the app.callback decorator.
#Place to add @app.callback Decorator
@app.callback( [ Output( component_id='plot1',    component_property='figure' ),
                 Output( component_id='plot2',    component_property='figure' ) ],
               [ Input(  component_id='region',   component_property='value'  ),
                 Input(  component_id='the-year', component_property='value'  ) ]
            )

   
#TASK 2.5: Add the callback function.
#Place to define the callback function .
def reg_year_display(input_region,input_year):
    
    #data
   #region_data = df[ df['Region'] == input_region ]
   #y_r_data = region_data[region_data['Year']==input_year]
   current_data = df [ ( df['Region'] == input_region ) & ( df['Year'] == input_year ) ].sort_values('Month_num')
    #Plot one - Monthly Average Estimated Fire Area
   
   est_data = current_data[['Month_num','Month','Estimated_fire_area']].groupby(['Month_num','Month']).sum().reset_index()
   print(est_data.head(14))
   fig1 = px.pie(est_data, values='Estimated_fire_area',  names='Month', title="{} : Monthly Average Estimated Fire Area in year {}".format(input_region,input_year))
   
     #Plot two - Monthly Average Count of Pixels for Presumed Vegetation Fires
   veg_data = current_data[['Month_num','Month','Count']].sort_values('Month_num').groupby(['Month_num','Month']).sum().reset_index()
   print("------------------------------------")
   print(veg_data.head(14))
   fig2 = px.bar(veg_data, x='Month', y='Count', title='{} : Average Count of Pixels for Presumed Vegetation Fires in year {}'.format(input_region,input_year))
    
   return [fig2, fig1]

if __name__ == '__main__':
    app.run()