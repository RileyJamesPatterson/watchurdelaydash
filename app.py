from dash import Dash, html, dcc, Input, Output
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import utils
from datetime import date,datetime,timedelta

external_stylesheets = ['watch.css']
logo_path='assets/logo.png'
app = Dash(__name__, external_stylesheets=external_stylesheets)
weather_table = {
    1: "Clear",
    2: "Fair",
    3: "Cloudy",
    4: "Overcast",
    5: "Fog",
    6: "Freezing Fog",
    7: "Light Rain",
    8: "Rain",
    9: "Heavy Rain",
    10: "Freezing Rain",
    11: "Heavy Freezing Rain",
    12: "Sleet",
    13: "Heavy Sleet",
    14: "Light Snow",
    15: "Snow",
    16: "Heavy Snow",
    17: "Rain Shower",
    18: "Heavy Rain Shower",
    19: "Sleet Shower",
    20: "Heavy Sleet Shower",
    21: "Snow Shower",
    22: "Heavy Snow Shower",
    23: "Lightning",
    24: "Hail",
    25: "Thunderstorm",
    26: "Heavy Thunderstorm",
    27: "Storm"
}
#import airport and flight data 
with open("assets/origin_airports.json") as file:
    departures=json.load(file) 

with open("assets/destination_airports.json") as file:
    arrival=json.load(file) 

airports = departures.copy()
airports.update(arrival)

# drop_d_dic=airports[["name","iata"]].rename(columns={"name":"label","iata":"value"}).to_dict('records')


#region ---Define Components

#departure point input form element
dep_input_element=html.Div([
    "Departure Point:",
    dcc.Dropdown(
        list(departures.keys()),
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
        id='arr_select',
        ),
    
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
    dest_iata = departureA

    # returns list of dics of connecting flights in the form {label:<name>,value:<iata>}
    return departures[dest_iata]["allowed_destination"]

#update airport map when departure or arrival dropdowns populated
@app.callback(
    Output('airportMap', 'figure'),
    Input('dep_select', 'value'),
    Input("arr_select","value"),
)
#Airport Marker Map
def genAirportMap(departureA,arrivalA):
    f_airports=pd.DataFrame.from_dict(airports,orient="index")
    
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

# Violin plot of historical data
@app.callback(
    Output('violinPlot', 'figure'),
    Input('dep_select', 'value'),
    Input("arr_select","value"),
    Input("date_input", "date"), #wire this up - DO WE WANT HOUR
)
def updateViolin(departureA,arrivalA,depDate):
    dep_iata = departureA
    arr_iata = arrivalA
    flights = utils.get_all_flights_for_airport(dep_iata, arr_iata)
    flights = pd.concat(flights)
 
    return px.violin(flights,y="ARR_DELAY",box=True,points="all")
    
#Parrallel catagories plot of historical data
@app.callback(
    Output('paraPlot', 'figure'),
    Input('dep_select', 'value'),
    Input("arr_select","value"),
    Input("date_input", "date"), #wire this up - DO WE WANT HOUR
)

def updateParaPlot(departureA,arrivalA,depDate):
    dep_iata = departureA
    flights=pd.read_json(f"assets/data/{dep_iata}_2019_flights.json")

    flights=flights[flights.DEST==arrivalA]
        
    return utils.getParacats(flights)

# Populate Departure Weather Data when input changes
@app.callback(
    Output('departureWeather', 'children'),
    Input("dep_select","value"),
    Input("date_input", "date"),
    Input('hour_input', 'value'),
)
def updateWeather(depA,depDate,hourInput):

    dep_iata = depA

    #Create datetime field from date and hour inputs
    datetime_obj=datetime.fromisoformat(str(depDate))
    
    delta= timedelta(hours=hourInput)
    flightDateTime=datetime_obj+delta
    
    #if input fields are populated get weather

    weather=utils.getWeather(departures[dep_iata]["lon"],departures[dep_iata]["lat"],flightDateTime)
    
    if np.isnan(weather["temp"]):
        weather["temp"]="Not Available"
    else:
        weather["temp"]=str(round(weather["temp"], 2))
    if np.isnan(weather["snow"]):
        weather["snow"]="Not Available"
    else:
        weather["snow"]=str(round(weather["snow"], 2))
    if np.isnan(weather["rain"]):
        weather["rain"]="Not Available"
    else:
        weather["rain"]=str(round(weather["rain"], 2))
    depWeather = [str(weather["temp"])+" C",weather["snow"],weather["rain"],weather_table[weather["code"]]]
   
    #create a list of html elements to return 
    divContents=[html.Td("Departure: "+dep_iata)]
    for i, arg in enumerate(depWeather):
        divContents.append(html.Td(arg))

    return divContents
    


#Populate Arrival Weather Data when input changes
@app.callback(
    Output('arrivalWeather', 'children'),
    Input("arr_select","value"),
    Input("date_input", "date"),
    Input('hour_input', 'value'),
)
def updateWeather(arrivalA,depDate,hourInput):

    arr_iata = arrivalA

    #Create datetime field from date and hour inputs
    datetime_obj=datetime.fromisoformat(str(depDate))
    
    delta= timedelta(hours=hourInput)
    flightDateTime=datetime_obj+delta
    
    #if input fields are populated get weather

    weather=utils.getWeather(departures[arr_iata]["lon"],departures[arr_iata]["lat"],flightDateTime)

    if np.isnan(weather["temp"]):
        weather["temp"]="Not Available"
    else:
        weather["temp"]=str(round(weather["temp"], 2))
    if np.isnan(weather["snow"]):
        weather["snow"]="Not Available"
    else:
        weather["snow"]=str(round(weather["snow"], 2))
    if np.isnan(weather["rain"]):
        weather["rain"]="Not Available"
    else:
        weather["rain"]=str(round(weather["rain"], 2))
    arrWeather = [weather["temp"]+" C",weather["snow"],weather["rain"],weather_table[weather["code"]]]
    #Create datetime field from date and hour inputs

    divContents=[html.Td("Arrival: "+arr_iata)]
    for arg in arrWeather:
        divContents.append(html.Td(arg))
    return (divContents)

    

# endregion

if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.1')

