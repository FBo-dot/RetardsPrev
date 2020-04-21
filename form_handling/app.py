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
from datetime import datetime

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