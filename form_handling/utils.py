# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 18:19:44 2020

@author: Fabretto
"""

import numpy as np
import pandas as pd

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