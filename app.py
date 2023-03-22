from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import date

external_stylesheets = ['watch.css']
logo_path='assets/logo.png'
app = Dash(__name__, external_stylesheets=external_stylesheets)

with open("assets/airports_of_concern.json") as file:
    airports=pd.read_json(file).T

iata_to_name=airports["name"].to_dict()
drop_d_dic=airports[["name","iata"]].rename(columns={"name":"label","iata":"value"}).to_dict('records')

#---Define Components

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
    "Departure window:",html.Br(),
    dcc.DatePickerRange(
        id="date_input",
        min_date_allowed=date.today(), #set this to todays date
        #max_date_allowed=pd.to_datetime(date.today())+pd.DateOffset(years=2),
        initial_visible_month=date.today(),)    
    ],
    className="header_input",
    )




#--- add components to virtual DOM
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
            style={'height': '100%'}
            )],
        id='rpanel2'),
    
    html.Div([
        #Weather Widget
        "Place Holder Weather Widget text"
        ],
        id='weatherWidget'),


], id="container")

#--- link DOM elements to data and events
#update arrival airport with departure airport connections

#clear arrival menu when departure dropdown changes
@app.callback(
        Output("arr_select","value"),
        Input("dep_select","value")
)
def clearArrivalAirport(_):
    return ""


#populate arrival dropdown when departure dropdown selected
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

#update airport map when deparure or arrival dropdowns populated
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
        title=departureA,
        geo_scope="usa",
        margin=dict(l=20, r=20, t=20, b=20),
        )
    return fig



if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.1')

