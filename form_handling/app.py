# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 14:30:40 2020

@author: Fabretto
"""

from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TimeField
from wtforms.validators import InputRequired, Length, AnyOf
from wtforms.fields.html5 import DateField

import pandas as pd
from datetime import datetime
from pandas.tseries.holiday import *
from pandas.tseries.offsets import CustomBusinessDay
import os
import pickle

from sklearn.base import BaseEstimator, TransformerMixin
# from .utils import SelectedFeatureDropper

current_path=os.getcwd()
saved_models_path = current_path + '\\final_models.pkl'
saved_predictors_data_path = current_path + '\\saved_predictors_data.pkl'

from sklearn.base import BaseEstimator, TransformerMixin

class SelectedFeatureDropper(BaseEstimator, TransformerMixin):
    def __init__(self, drop_first_feature=True): # Assumes first feature is 'DEP_DELAY'
        self.drop_first_feature = drop_first_feature
    def fit(self, X, y=None):
        return self # nothing else todo
    def transform(self, X, y=None):
        if self.drop_first_feature:
#            pdb.set_trace()
            X = X.iloc[:,1:]
        return X

with open(saved_models_path,'rb') as f:
    saved_full_pipeline = pickle.load(f)
    saved_final_models = pickle.load(f)
    saved_model_names = pickle.load(f)
    saved_train_rmses = pickle.load(f)
    saved_final_rmses = pickle.load(f)
    saved_full_pipeline_1 = pickle.load(f)
    saved_final_models_1 = pickle.load(f)
    saved_model_names_1 = pickle.load(f)
    saved_train_rmses_1 = pickle.load(f)
    saved_final_rmses_1 = pickle.load(f)
    
with open(saved_predictors_data_path, 'rb') as f:
    saved_target_attribs = pickle.load(f)
    saved_carrier_df = pickle.load(f)
    saved_airports_df = pickle.load(f)
    saved_arr_time_blk_labels = pickle.load(f)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisisasecret!'

class LoginForm(FlaskForm):
    """
    username = StringField('username',
                           validators=[InputRequired('A username is required!'),
                                       Length(min=5, max=10, message='Must be between 5 and 10 characters.')])
    password = PasswordField('password',
                             validators=[InputRequired('Password is required!'),
                                         AnyOf(values=['password', 'secret'])])
    """
    dep_date = DateField('departure date', format='%Y-%m-%d',
                         validators=[InputRequired('A departure date is required')])
    dep_time = TimeField('departure time', format='%H:%M',
                         validators=[InputRequired('Time required as hh:mm')])

def build_X_features(dep_datetime, arr_datetime, origin='JFK', destination='ATL', carrier='WN', dep_delay=16):
    query_df = pd.DataFrame({
        'MONTH': dep_datetime.month,
        'DAY_OF_MONTH': dep_datetime.day,
        'DAY_OF_WEEK': dep_datetime.weekday() + 1,  # Mo=1, ..., Su=7
        'CRS_DEP_TIME': dep_datetime.hour * 100 + dep_datetime.min,
        'CRS_ARR_TIME': arr_datetime.hour * 100 + arr_datetime.min,
        'OriginSizes': 1,
#        saved_airports_df[saved_airports_df['AirportID'] ==
#                          origin]['OriginSizes'].values,
        'DestSizes': 1,
#        [saved_airports_df['AirportID'] ==
#                          destination]['DestSizes'].values,
        'CarrierSizes': 1,
#        saved_carrier_df[saved_carrier_df['CARRIER'] == carrier]
#        ['CarrierSizes'].values,
        'DAY_OF_YEAR': dep_datetime.timetuple().tm_yday,
        'WEEK_NUM': dep_datetime.isocalendar()[1],
        'DEP_DELAY': dep_delay,
        'CRS_ELAPSED_TIME': (arr_datetime - dep_datetime).seconds / 60,
        'HDAYS': 1,
 #       hdays,
        'ARR_TIME_BLK':'00-05',
#        arr_time_blk,
        'CARRIER': carrier
    })
    return query_df

@app.route('/form', methods=['GET', 'POST'])
def form():
    form = LoginForm()
    
    if form.validate_on_submit():
        dep_datetime = datetime.combine(form.dep_date.data, form.dep_time.data)
        dep_datetime_str = dep_datetime.strftime('%Y-%m-%d %H:%M')
        result_str = '<h1>'
        result_str = result_str + 'The departure date and time is {}.'.format(dep_datetime_str)
        return  result_str
    return render_template('form.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)