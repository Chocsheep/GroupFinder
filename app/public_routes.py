from flask import Flask, render_template, redirect, request, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

from app import app
from app.forms import validate_signup_form
import app.db as db


@app.get('/')
def home():
    return render_template('public_pages/home.html')

@app.get('/home')
def redirect_homepage():
    return redirect(url_for('home'))

@app.post('/signup')
def process_signup(): 
    # Collect form data
    form_data = dict(request.form)
    password = request.form.get('new_password')

    # Validate form
    errors = validate_signup_form(form_data)
    
    # If there are errors, re-render the form and display them
    if errors:
        return render_template('public_pages/signup.html', errors=errors, form_data=form_data)
    else:
        password_hash = generate_password_hash(password)
        # Add the user into the database
        sql = 'INSERT INTO Users (username, password_hash) VALUES (?, ?)'
        data = (form_data['username'], password_hash)
        db.edit_db(sql, data)

        return redirect(url_for('show_login_form'))


@app.get('/login')
def show_login_form():
    """Displays the login form"""
    if 'user_id' in session:
        return redirect(url_for('show_dashboard'))
    else:
        return render_template('public_pages/login.html')

@app.get('/signup')
def show_signup_form():
    """Displays the login form"""
    if 'user_id' in session:
        return redirect(url_for('show_dashboard'))
    else:
        return render_template('public_pages/signup.html')
    

@app.post('/login')
def login_user():
    """Processes the login attempt"""
    
    # Get form details
    username = request.form.get('username')
    password = request.form.get('password')


    # Get the user details associated with the username entered
    sql = 'SELECT * FROM Users WHERE username = ?'
    data = (username,)
    user = db.query_one(sql, data)

    if not user:
        # No user with that username exists
        valid_login = False

    elif check_password_hash(user['password_hash'], password):
        # Login successful - store user id and nickname in session
        valid_login = True
        session['user_id'] = user['user_id']
        session['username'] = user['username']
    else:
        # Invalid password
        valid_login = False

    if valid_login:
        # Redirect to the tasks home page
        flash(f"Successfully logged in. Welcome to OutfitProject!")
        return redirect(url_for('show_dashboard'))
    else:
        # Re-render the login page
        return render_template('public_pages/login.html', login_failed=True)



def handle_errors(error):
    if 'user_id' in session:
        logged_in = True
        base_template = "base/user_base.html"
    else:
        logged_in = False
        base_template = "base/public_base.html"

    return render_template('public_pages/error.html',
        base_template=base_template,
        logged_in=logged_in)