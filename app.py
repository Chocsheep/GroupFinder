
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
    students = conn.execute('SELECT * FROM Students').fetchall()
    marks = conn.execute("SELECT * FROM Marks").fetchall()
    conn.close()
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template("index.html", today=today, students=students, marks=marks)

@app.route("/about")
def about():
    html = """
        <h1>Welcome to my about page</h1>
        <p>I'm an epic coder</p>
        <a href="/">Go to home page</a>
    """
    return html

@app.route('/add', methods=['POST'])
def add():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    DOB = request.form['dob']
    conn = get_db_connection()
    conn.execute('INSERT INTO Students (firstname, lastname, dob) VALUES (?, ?, ?)', (firstname, lastname, DOB))
    conn.commit()
    conn.close()
    return redirect('/#heading')

@app.route('/addmark', methods=['POST'])
def addmark():
    studid = request.form['studid']
    subject = request.form['subject']
    mark = request.form['mark']
    conn = get_db_connection()
    conn.execute('INSERT INTO Marks (student_id, subject, mark) VALUES (?, ?, ?)', (studid, subject, mark))
    conn.commit()
    conn.close()
    return redirect('/marks')

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.execute('DELETE FROM marks WHERE student_id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/#heading')

@app.route('/delete_mark/<int:id>')
def delete_mark(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM marks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/marks')

@app.route("/marks")
def Marks():
    conn = get_db_connection()
    markData = conn.execute("SELECT id, student_id, subject, mark, date_created FROM Marks ORDER BY student_id").fetchall()
    return render_template("marks.html", marks = markData)

@app.route("/student/<id>")
def Student(id):
    conn = get_db_connection()
    
    studentData = conn.execute(f"SELECT * FROM Students WHERE id={id}").fetchone()
    
    markData = conn.execute(f"SELECT * FROM Marks WHERE student_id={id}").fetchall()
    
    html =  f"""
        The student infornmation is <br>
        Firstname: {studentData['firstname']}<br>
        Lastname: {studentData['lastname']}<br>
        DOB: {studentData['dob']}<br>
    """
    for result in markData:
        html += f"Mark for {result['subject']} is {result['mark']} <br>"
        
    return render_template("student.html", marks=markData, student=studentData)

if __name__ == '__main__':
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS Students
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    firstname TEXT NOT NULL,
                    lastname TEXT NOT NULL,
                    dob TEXT NOT NULL,
                    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS Marks
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    subject TEXT NOT NULL,
                    mark INTEGERL,
                    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.close()
    app.run(debug=True)