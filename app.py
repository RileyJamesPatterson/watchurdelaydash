from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import utils
from datetime import date

external_stylesheets = ['watch.css']
logo_path='assets/logo.png'
app = Dash(__name__, external_stylesheets=external_stylesheets)

#import airport and flight data 
with open("assets/airports_of_concern.json") as file:
    airports=pd.read_json(file).T #PLACEHOLDER NEED REAL DATA

with open("assets/DTW_2021_flights.json") as file:
    flights=pd.read_json(file) #PLACEHOLDER NEED REAL DATA

iata_to_name=airports["name"].to_dict()
drop_d_dic=airports[["name","iata"]].rename(columns={"name":"label","iata":"value"}).to_dict('records')


#region ---Define Components

#departure point input form element
dep_input_element=html.Div([
    "Departure Point:",
    dcc.Dropdown(
        drop_d_dic,
        'Departure Airport',
        id='dep_select',
        ),
        
   ],
    className="header_input",
    )

#arrival point input form element
arr_input_elemnet=html.Div([
    "Arrival:",
    dcc.Dropdown(
        id='arr_select' ),
    
    ],
    className="header_input",
    )

#departure date input form element
date_input_element=html.Div([
    "Departure Date:",html.Br(),
    dcc.DatePickerSingle(
        id="date_input",
        min_date_allowed=date.today(), #set this to todays date
        max_date_allowed=pd.to_datetime(date.today())+pd.DateOffset(weeks=2),
        date=date.today(),
    )
          
    ],
    className="header_input",
    )
# endregion

# region --- Add components to virtual DOM
app.layout = html.Div([
    #header
    html.Div([
        html.Img(src=logo_path),
        dep_input_element,
        arr_input_elemnet,
        date_input_element,
        ],
        id="app-header"
        ),

    
    html.Div([
        #left Panel
        dcc.Graph(
            id='airportMap',
            style={'height': '100%'}
        )
        ],
        id="lpanel"),

    html.Div([
        #right panel
        dcc.Graph(
            style={'height': '100%'}
            )
        ],
        id='rpanel1'),
    html.Div([
        dcc.Graph(
            id="violinPlot",
            style={'height': '100%'}
            )],
        id='rpanel2'),
    
    html.Div([
        #Weather Widget
        "Place Holder Weather Widget text"
        ],
        id='weatherWidget'),


], id="container")
# endregion

#region --- Define Events and States
#clear arrival menu when departure dropdown changes
@app.callback(
        Output("arr_select","value"),
        Input("dep_select","value")
)
def clearArrivalAirport(_):
    return ""


#populate arrival dropdown when departure dropdown selected with airport connections
@app.callback(
     Output("arr_select","options"),
     Input("dep_select","value"),   
)
def genConnections(departureA):
    #updates arrival airport dropdown label/value options
    selected_row=airports[airports["iata"]==departureA]
    #return blank if departure airport not in data - prevents start up warning
    if departureA not in airports.index:
        return {}
    connections=selected_row.allowed_destination[0]
    # returns list of dics of connecting flights in the form {label:<name>,value:<iata>}
    return airports.loc[connections,["name","iata"]].rename(columns={"name":"label","iata":"value"}).to_dict('records')

#update airport map when departure or arrival dropdowns populated
@app.callback(
    Output('airportMap', 'figure'),
    Input('dep_select', 'value'),
    Input("arr_select","value"),
)
#Airport Marker Map
def genAirportMap(departureA,arrivalA):
    f_airports=airports.copy()
    
    
    #creates a column with map color based on selection status
    f_airports["selection"]="black"
    f_airports.loc[departureA,"selection"]="red"
    connections=f_airports.loc[departureA,"allowed_destination"]
    f_airports.loc[connections,"selection"]="aqua"
    f_airports.loc[arrivalA,"selection"]="orange"

    #Once user has selected a departure airport, non-connecting airports dropped from map
    if departureA != "Departure Airport":
        show_only=[*connections,departureA]
        f_airports=f_airports.loc[show_only]
    fig=go.Figure(data=go.Scattergeo(
        lon=f_airports["lon"],
        lat=f_airports["lat"],
        text=f_airports["name"],
       
        mode="markers",
        marker_color=f_airports["selection"],
        ))
    fig.update_layout(
    #    title=departureA,
        geo_scope="usa",
        margin=dict(l=20, r=20, t=20, b=20),
        )
    return fig

#Violin plot of historical data
@app.callback(
    Output('violinPlot', 'figure'),
    Input('dep_select', 'value'),
    Input("arr_select","value"),
    Input("date_input", "date"),
)
def updateViolin(departureA,arrivalA,depDate):
    f_flights=flights.copy()
    if (departureA in f_flights.ORIGIN.values) and (arrivalA in f_flights.DEST.values):
        # if inputs are populated
        f_flights=f_flights.loc[(flights.ORIGIN==departureA) & (flights.DEST==arrivalA)]
        fig=px.violin(f_flights,y="ARR_DELAY",box=True,points="all")
        return fig

    else:
        #failure case - inputs not populated
        f_flights=f_flights.loc[(flights.ORIGIN==departureA) & (flights.DEST==arrivalA)]
        fig=px.violin(f_flights,y="ARR_DELAY",box=True,points="all")
        return fig


#Populate Weather Data when input changes
@app.callback(
    Output('weatherWidget', 'children'),
    Input('dep_select', 'value'),
    Input("arr_select","value"),
    Input("date_input", "date"),
)

def updateWeather(departureA,arrivalA,depDate):
    #if input fields are populated get weather
    if (departureA in airports.index) and (arrivalA in airports.index):
        depWeather=utils.getWeather(airports.loc[departureA].lon,airports.loc[departureA].lat,depDate)

    #else return blank state
    else:
        depWeather="Please Input Departure point, Arrival Point and Date to generate weather"
    return ([arg for arg in depWeather])







# endregion

if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.1')

