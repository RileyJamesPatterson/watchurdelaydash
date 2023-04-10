from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import utils
from datetime import date,datetime,time,timedelta

external_stylesheets = ['watch.css']
logo_path='assets/logo.png'
app = Dash(__name__, external_stylesheets=external_stylesheets)

#import airport and flight data 
with open("assets/airports_of_concern.json") as file:
    airports=pd.read_json(file).T #PLACEHOLDER NEED REAL DATA polars goes here

with open("assets/DTW_2021_flights.json") as file:
    flights=pd.read_json(file) #PLACEHOLDER NEED REAL DATA polars goes here

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
    ),
    "Departure hour (0-23):",html.Br(),
    dcc.Input(
    id="hour_input",
    type="number",
    min=0,
    max=23,
    value=13,
    ),
          
    ],
    id="departure_date",
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
            id="violinPlot",
            style={'height': '100%'}
            )
        ],
        id='rpanel1'),
    html.Div([
        dcc.Graph(
            id="paraPlot",
            style={'height': '100%'}
            )],
        id='rpanel2'),
    
    html.Table([
        #Weather Widget
        html.Tr([
            html.Th("Airport"),
            html.Th(html.Img(src="assets/smallTempIcon.png")),
            html.Th(html.Img(src="assets/smallSnowIcon.png")),
            html.Th(html.Img(src="assets/smallRainIcon.png")),
            html.Th(html.Img(src="assets/smallVisibilIcon.png")),
            ],id="weatherIcons"),
        html.Br(),
        html.Tr([html.Td("1"),html.Td("1"),html.Td("1"),html.Td("1"),html.Td("1")],id="departureWeather"),
        html.Br(),
        html.Tr([html.Td("1"),html.Td("1"),html.Td("1"),html.Td("1"),html.Td("1")],id="arrivalWeather"),
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
    Input("date_input", "date"), #wire this up - DO WE WANT HOUR
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
    
#Parrallel catagories plot of historical data
@app.callback(
    Output('paraPlot', 'figure'),
    Input('dep_select', 'value'),
    Input("arr_select","value"),
    Input("date_input", "date"), #wire this up - DO WE WANT HOUR
)

def updateParaPlot(departureA,arrivalA,depDate):
    f_flights=flights.copy()
    if (departureA in f_flights.ORIGIN.values) and (arrivalA in f_flights.DEST.values):
        # if inputs are populated
        f_flights=f_flights.loc[(flights.ORIGIN==departureA) & (flights.DEST==arrivalA)]
        return utils.getParacats(f_flights)

    else:
        #failure case - inputs not populated
        f_flights=f_flights.loc[(flights.ORIGIN==departureA) & (flights.DEST==arrivalA)]
        
        return utils.getParacats(f_flights)

#Populate Departure Weather Data when input changes
@app.callback(
    Output('departureWeather', 'children'),
    Input("dep_select","value"),
    Input("date_input", "date"),
    Input('hour_input', 'value'),
)
def updateWeather(depA,depDate,hourInput):

    #Create datetime field from date and hour inputs
    datetime_obj=datetime.fromisoformat(str(depDate))
    delta= timedelta(hours=hourInput)
    flightDateTime=datetime_obj+delta
    
    #if input fields are populated get weather
    if (depA in airports.index):
        #CURRENTLY IF YOU MANUALLY INPUT DATE YOU GET A WARNING ABOUT ISO STRING
        depWeather=utils.getWeather(airports.loc[depA].lon,airports.loc[depA].lat,flightDateTime)
        #create a list of html elements to return 
        divContents=[html.Td("Departure: "+depA)]
        for arg in depWeather:
            divContents.append(html.Td(arg))
        return (divContents)
    
    #else return blank state
    else:
        return html.Td("Please Input Departure Airport and Date to Generate Weather",colSpan=5)


#Populate Arrival Weather Data when input changes
@app.callback(
    Output('arrivalWeather', 'children'),
    Input("arr_select","value"),
    Input("date_input", "date"),
    Input('hour_input', 'value'),
)
def updateWeather(arrivalA,depDate,hourInput):

    #Create datetime field from date and hour inputs
    datetime_obj=datetime.fromisoformat(str(depDate))
    delta= timedelta(hours=hourInput)
    flightDateTime=datetime_obj+delta
    
    #if input fields are populated get weather
    if (arrivalA in airports.index):
        #CURRENTLY IF YOU MANUALLY INPUT DATE YOU GET A WARNING ABOUT ISO STRING
        depWeather=utils.getWeather(airports.loc[arrivalA].lon,airports.loc[arrivalA].lat,flightDateTime)
        #create a list of html elements to return 
        divContents=[html.Td("Arrival: "+arrivalA)]
        for arg in depWeather:
            divContents.append(html.Td(arg))
        return (divContents)
    
    #else return blank state
    else:
        return html.Td("Please Input Arrival Airport and Date to Generate Weather",colSpan=5)

    



# endregion

if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.1')

