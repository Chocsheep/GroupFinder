
from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import random
import os

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(__file__), 'database1.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    conn = get_db_connection()
#    students = conn.execute('SELECT * FROM Students').fetchall()
#    marks = conn.execute("SELECT * FROM Marks").fetchall()
#    conn.close()
#    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template("index.html")

if __name__ == '__main__':
    conn = get_db_connection()
#    conn.execute('''CREATE TABLE IF NOT EXISTS Students
#                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                    firstname TEXT NOT NULL,
#                    lastname TEXT NOT NULL,
#                    dob TEXT NOT NULL,
#                    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
#    conn.execute('''CREATE TABLE IF NOT EXISTS Marks
#                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                    student_id INTEGER,
#                    subject TEXT NOT NULL,
#                    mark INTEGERL,
#                    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.close()
    app.run(debug=True)