'''
This file initialises the flask app, sets relevant configuration variables, and imports the routes for the application.
'''

from flask import Flask
import os
from datetime import date
import sqlite3

# Create app
app = Flask(__name__)

# Define configuration variables
app.config['DATABASE'] = 'group.db'

app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
# app.config['SECRET_KEY'] = os.urandom(24)
# change to that when its time ^^
app.config['SECRET_KEY'] = 'temp'

def init_db():
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

# Initialise database
init_db()

# Import routes
from app import user_routes, public_routes

# checking database intialised properly
@app.route("/dbcheck")
def db_check():
    conn = sqlite3.connect(app.config['DATABASE'])
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    conn.close()
    return str([t['name'] for t in tables])
