'''
This file initialises the flask app, sets relevant configuration variables, and imports the routes for the application.
'''

from flask import Flask
import os
from datetime import date

# Create app
app = Flask(__name__)

# Define configuration variables
app.config['DATABASE'] = 'group.db'

app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
# app.config['SECRET_KEY'] = os.urandom(24)
# change to that when its time ^^
app.config['SECRET_KEY'] = 'temp'

# Import routes
from app import user_routes, public_routes
