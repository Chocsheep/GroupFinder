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

# home page -> essentially what is first loaded when a user logs in to the website 
@app.route("/")
def home():
    conn = get_db_connection()
    conn.close()
    return render_template("index.html")
 
if __name__ == '__main__':
    conn = get_db_connection()
    conn.close()

    # Railway injects its own port via environment variable
    port = int(os.environ.get("PORT", 5000))

    # lets Railway's network reach the app
    app.run(debug=False, host="0.0.0.0", port=port)
 
