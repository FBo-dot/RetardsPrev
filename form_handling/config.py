# -*- coding: utf-8 -*-
"""
Created on Sun May  3 15:25:50 2020

@author: Fabretto
"""

import os

# Datafiles names and folder initialization
datafiles_folder = 'datafiles'

PREDICTORS_DATA_FILE = os.path.join(datafiles_folder, 'saved_predictors_data.joblib')
AIRPORTS_LIST_FILE = os.path.join(datafiles_folder, 'L_AIRPORT.csv')
CARRIERS_LIST_FILE = os.path.join(datafiles_folder, 'L_UNIQUE_CARRIERS.csv')

MODELS_FILE = os.path.join(datafiles_folder, 'final_models.joblib')