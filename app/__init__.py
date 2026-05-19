'''
This file initialises the flask app, sets relevant configuration variables, and imports the routes for the application.
'''

from flask import Flask
import os
from datetime import date
import sqlite3
from flask_socketio import SocketIO

# Create app
app = Flask(__name__)

# Define configuration variables
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'group.db')

app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
# app.config['SECRET_KEY'] = os.urandom(24)
# change to that when its time ^^
app.config['SECRET_KEY'] = 'temp'

socketio = SocketIO(app)
# web sockets for real-time chat function

def init_db():
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        c.executescript('''
            CREATE TABLE IF NOT EXISTS Users (
                userid      INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT NOT NULL,
                discord     TEXT,
                password    TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS Groups (
                groupid     INTEGER PRIMARY KEY AUTOINCREMENT,
                owner       INTEGER NOT NULL,
                name        TEXT NOT NULL,
                description TEXT,
                max_people  INTEGER,
                location    TEXT,
                FOREIGN KEY (owner) REFERENCES Users(userid)
            );
            CREATE TABLE IF NOT EXISTS Tags (
                tagid       INTEGER PRIMARY KEY AUTOINCREMENT,
                tagname     TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS GroupTags (
                tagid       INTEGER NOT NULL,
                groupid     INTEGER NOT NULL,
                PRIMARY KEY (tagid, groupid),
                FOREIGN KEY (tagid)   REFERENCES Tags(tagid),
                FOREIGN KEY (groupid) REFERENCES Groups(groupid)
            );
            CREATE TABLE IF NOT EXISTS GroupMembers (
                userid      INTEGER NOT NULL,
                groupid     INTEGER NOT NULL,
                PRIMARY KEY (userid, groupid),
                FOREIGN KEY (userid)  REFERENCES Users(userid),
                FOREIGN KEY (groupid) REFERENCES Groups(groupid)
            );
            CREATE TABLE IF NOT EXISTS Messages (
                messageid   INTEGER PRIMARY KEY AUTOINCREMENT,
                groupid     INTEGER NOT NULL,
                userid      INTEGER NOT NULL,
                content     TEXT NOT NULL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (groupid) REFERENCES Groups(groupid),
                FOREIGN KEY (userid)  REFERENCES Users(userid)
            );
            INSERT OR IGNORE INTO Tags (tagname) VALUES
                ('Math1131'),
                ('Math1141'),
                ('Math1081'),
                ('Comp1511'),
                ('Comp2521'),
                ('Comp1531'),
                ('Comp1521'),
                ('Phys1121'),
                ('Math1151');
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

# Initialise database
init_db()

# Import routes
from app import user_routes, public_routes
