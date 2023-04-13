import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from scipy.stats import poisson



def get_prediction(model, date_features, k, inputs):


    np.seterr(divide = 'ignore') 

    x = date_features[date_features.date == inputs['date']].copy()
    
    x['dep_hour_g'] = np.where((inputs['dep_hour'] > 22) | (inputs['dep_hour'] < 5), 25, inputs['dep_hour'])
    x['origin'] = inputs['origin']
    x['dest'] = inputs['dest']
    x['origin_code'] = inputs['origin_code']
    x['dest_code'] = inputs['dest_code']
    x['origin_temperature_adj'] = np.log(abs(inputs['origin_temperature'] - 10) + 0.01)
    x['dest_temperature_adj'] = np.log(abs(inputs['dest_temperature'] - 10) + 0.01)
    x['origin_precipitation'] = inputs['origin_total_precipitation'] > 0
    x['dest_precipitation'] = inputs['dest_total_precipitation'] > 0
    x['origin_total_precipitation_adj'] = np.around(np.where(x['origin_precipitation'], np.log(inputs['origin_total_precipitation']), -99), 2)
    x['dest_total_precipitation_adj'] = np.around(np.where(x['dest_precipitation'], np.log(inputs['dest_total_precipitation']), -99), 2)
    
    mean = model.get_prediction(x).summary_frame(0.05).loc[0,'mean']
    pmf = poisson.pmf(np.arange(0, k), mu=mean)
    
    return mean, pmf



