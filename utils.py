import glob
import os
import pandas as pd
import meteostat as ms
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta



def getWeather(lon,lat,date):
    #Takes longitude of airport, latitude of airporte and datetime of departure,
    #returns list of [precipitation ,snow,temperature and visbility formated as strings

    #placeholder for api call
    start = date - timedelta(hours=1)
    end = date + timedelta(hours=1)
    point = ms.Point(lat, lon)
    weather = ms.Hourly(point, start, end).fetch()
    temp = np.nanmean(weather.temp)
    wind = np.nanmean(weather.wspd)
    humidity = np.nanmean(weather.rhum)
    precip = np.nanmean(weather.prcp)
    snow = np.nanmean(weather.snow)
    code = int(np.nanmax(weather.coco))

    return {"temp":temp,"wind": wind,"rhum": humidity,"rain": precip,"snow": snow, "code":code}

def getParacats(flights):
    '''Takes a dataframe of flights and returns a a plotly parrallel catagory figure
    '''
        #bucket arrival delay into integer coding
    flights["BUCKETED_DELAY"]=pd.cut(
        flights["ARR_DELAY"].fillna(9999), #replace nan with dummy var
        bins=[-100,0,15,30,9998,9999], #bins correspend to [ontime,0-15,15-30,30+,cancelled]
        labels=[0,1,2,3,4]   #CAN WE PREPROCESS THIS
    )


    #Create dimensions for plot
    carrier_dim=go.parcats.Dimension(
        values=flights["OP_UNIQUE_CARRIER"],
        #categoryoreder="category ascending",
        label="Carrier")

    delay_dim=go.parcats.Dimension(
        values=flights["BUCKETED_DELAY"],
        label="Delay",
        categoryorder="array",
        categoryarray=[0,1,2,3,4],
        ticktext=["On time", "0-15 Minutes","15-30 mins","30+ mins","Cancelled"]
        )

    #create parcats trace
    color=flights["BUCKETED_DELAY"]
    colorscale=["seagreen","khaki","orange","lightsalmon","darkred"]
    fig=go.Figure(
        data=[
            go.Parcats(
            dimensions=[carrier_dim,delay_dim],
            line={"color":color,"colorscale":colorscale},
            hoveron="color",
            hoverinfo="count + probability",
            labelfont={"size": 18,},
            tickfont={"size": 16, },
            arrangement="freeform"
            )
        ]
    )
    return fig

def get_all_flights_for_airport(dep_airport_iata, arr_airport_iata):
    for file in glob.glob(f"assets/data/{dep_airport_iata}_*_flights.json"):
        df = pd.read_json(file)
        df = df[df["DEST"] == arr_airport_iata]
        yield df

        

