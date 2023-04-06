
import pandas as pd

import plotly.graph_objects as go


def getWeather(lon,lat,date):
    #placeholder for api call
    return (lon,lat, date)

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
    colorscale=["seagreen","khaki","orange","red","darkred"]
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
