# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 14:30:40 2020

@author: Fabretto
"""

from flask import Flask, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import TimeField, SelectField, IntegerField
from wtforms.validators import InputRequired
from wtforms.fields.html5 import DateField

import pandas as pd
from datetime import datetime
from pandas.tseries.holiday import *
from pandas.tseries.offsets import CustomBusinessDay
import os

import joblib

import json

from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder, MinMaxScaler, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

"""
current_path=os.getcwd()
saved_predictors_data_path = os.path.join(current_path, 'saved_predictors_data.joblib')
airports_list_path = os.path.join(current_path, 'L_AIRPORT.csv')
carriers_list_path = os.path.join(current_path, 'L_UNIQUE_CARRIERS.csv')

saved_models_path = os.path.join(current_path, 'final_models.joblib')
"""

app = Flask(__name__.split('.')[0])
app.config['SECRET_KEY'] = 'Thisisasecret!'
# app.config['SERVER_NAME'] = '127.0.0.1:5000/'


datafiles_path = app.static_folder + '/datafiles'

saved_predictors_data_path = os.path.join(datafiles_path, 'saved_predictors_data.joblib')
airports_list_path = os.path.join(datafiles_path, 'L_AIRPORT.csv')
carriers_list_path = os.path.join(datafiles_path, 'L_UNIQUE_CARRIERS.csv')

saved_models_path = os.path.join(datafiles_path, 'final_models.joblib')

"""
with app.app_context():
    saved_predictors_data_path = url_for('static', filename='datafiles/saved_predictors_data.joblib', _external=True)
    airports_list_path = url_for('static', filename='datafiles/L_AIRPORT.csv', _external=True)
    carriers_list_path = url_for('static', filename='datafiles/L_UNIQUE_CARRIERS.csv', _external=True)
    
    saved_models_path = url_for('static', filename='datafiles/final_models.joblib', _external=True)
"""

with open(saved_predictors_data_path,'rb') as f:
    saved_target_attribs = joblib.load(f)
    saved_carrier_df = joblib.load(f)
    saved_airports_df = joblib.load(f)
    saved_arr_time_blk_labels = joblib.load(f)
    
with open(saved_models_path,'rb') as f:
    saved_full_pipeline = joblib.load(f)
    saved_final_models = joblib.load(f)
    saved_model_names = joblib.load(f)
    saved_train_rmses = joblib.load(f)
    saved_final_rmses = joblib.load(f)
    saved_full_pipeline_1 = joblib.load(f)
    saved_final_models_1 = joblib.load(f)
    saved_model_names_1 = joblib.load(f)
    saved_train_rmses_1 = joblib.load(f)
    saved_final_rmses_1 = joblib.load(f)

l_carriers = pd.read_csv(carriers_list_path)
l_airports = pd.read_csv(airports_list_path)

carriers = pd.merge(saved_carrier_df, l_carriers, left_on=['CARRIER'], right_on=['Code'], sort=True, how='left')
carriers.sort_values(by=['Description'], inplace=True)
carrier_tuples = [row for row in carriers[['CARRIER', 'Description']].itertuples(index=False)]

airports = pd.merge(saved_airports_df, l_airports, left_on=['AirportID'], right_on=['Code'], sort=True, how='left')
airports.sort_values(by=['Description'], inplace=True)
airport_tuples = [row for row in airports[['AirportID', 'Description']].itertuples(index=False)]

class LoginForm(FlaskForm):

    dep_date = DateField('departure date', format='%Y-%m-%d',
                         validators=[InputRequired('A departure date is required')])
    dep_time = TimeField('departure time', format='%H:%M',
                         validators=[InputRequired('Time required as hh:mm')])
    arr_date = DateField('arrival date', format='%Y-%m-%d',
                         validators=[InputRequired('An arrival date is required')])
    arr_time = TimeField('arrival time', format='%H:%M',
                         validators=[InputRequired('Time required as hh:mm')])
    carrier = SelectField('carrier', choices=carrier_tuples,
                         validators=[InputRequired('Select a carrier')])
    origin = SelectField('origin', choices=airport_tuples,
                         validators=[InputRequired('Select an origin airport')])
    destination = SelectField('destination', choices=airport_tuples,
                         validators=[InputRequired('Select a destination airport')])
    dep_delay = IntegerField('departure delay in minutes',
                         validators=[InputRequired('The departure delay is required')])

def build_X_features(dep_datetime, arr_datetime, origin='JFK', destination='ATL', carrier='WN', dep_delay=16):
    return pd.DataFrame({
        'MONTH': dep_datetime.month,
        'DAY_OF_MONTH': dep_datetime.day,
        'DAY_OF_WEEK': dep_datetime.weekday() + 1,  # Mo=1, ..., Su=7
        'CRS_DEP_TIME': dep_datetime.hour * 100 + dep_datetime.minute,
        'CRS_ARR_TIME': arr_datetime.hour * 100 + arr_datetime.minute,
        'OriginSizes': saved_airports_df[saved_airports_df['AirportID'] == origin]['OriginSizes'].values,
        'DestSizes': saved_airports_df[saved_airports_df['AirportID'] == destination]['DestSizes'].values,
        'CarrierSizes': saved_carrier_df[saved_carrier_df['CARRIER'] == carrier]['CarrierSizes'].values,
        'DAY_OF_YEAR': dep_datetime.timetuple().tm_yday,
        'WEEK_NUM': dep_datetime.isocalendar()[1],
        'DEP_DELAY': dep_delay,
        'CRS_ELAPSED_TIME': (arr_datetime - dep_datetime).seconds / 60,
        'HDAYS': min(abs(dep_datetime - USFederalHolidayCalendar.holidays(USFederalHolidayCalendar))).days,
        'ARR_TIME_BLK': pd.cut([arr_datetime.hour], bins=[0] + list(range(6,25,1)),
                               right=False, labels=saved_arr_time_blk_labels),
        'CARRIER': carrier})

def predict_delay(X, pipeln, model):
    return model.predict(pipeln.transform(X))[0]

@app.route('/', methods=['GET', 'POST'])
@app.route('/form', methods=['GET', 'POST'])
def form():
    form = LoginForm()
    
    if form.validate_on_submit():
        dep_datetime = datetime.combine(form.dep_date.data, form.dep_time.data)
        dep_datetime_str = dep_datetime.strftime('%Y-%m-%d %H:%M')
        arr_datetime = datetime.combine(form.arr_date.data, form.arr_time.data)
        arr_datetime_str = arr_datetime.strftime('%Y-%m-%d %H:%M')
        result_str = '<u1>'
        result_str = result_str + '<li>The departure date and time is {}.</li>'.format(dep_datetime_str)
        result_str = result_str + '<li>The arrival date and time is {}.</li>'.format(arr_datetime_str)
        result_str = result_str + '</u1>'
#        query_df =  build_X_features(dep_datetime, arr_datetime)
        X_features = build_X_features(dep_datetime,
                                      arr_datetime,
                                      form.origin.data,
                                      form.destination.data,
                                      form.carrier.data,
                                      form.dep_delay.data)
        a_priori_prediction = predict_delay(X_features, saved_full_pipeline, saved_final_models[0])
        a_priori_error = saved_final_rmses[0]
        cond_prediction = predict_delay(X_features, saved_full_pipeline_1, saved_final_models_1[0])
        cond_error = saved_final_rmses_1[0]
        print(a_priori_prediction)
        print(a_priori_error)
        print(cond_prediction)
        print(cond_error)
        return render_template('resultat.html',
                               carrier=carriers[carriers['CARRIER']==form.carrier.data]['Description'].values[0],
                               origin=airports[airports['AirportID']==form.origin.data]['Description'].values[0],
                               destination=airports[airports['AirportID']==form.destination.data]['Description'].values[0],
                               dep_dt=dep_datetime,
                               arr_dt=arr_datetime,
                               a_forecast=a_priori_prediction,
                               a_error=a_priori_error,
                               c_forecast=cond_prediction,
                               c_error=cond_error)
#        return json.dumps(carrier_tuple)
#        return carriers.to_json(orient="records")
#        return X_features.to_json(orient="records")
#        return  result_str
    return render_template('form.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)