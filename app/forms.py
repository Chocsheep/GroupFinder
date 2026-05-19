
import app.db as db
from flask import session, abort
from werkzeug.security import generate_password_hash, check_password_hash

def validate_signup_form(form_data):
    """Returns a dictionary of errors (if there are any) associated with the sign up form on StudyCity"""

    # Set up errors dictionary
    errors = {}

    # Get the variables
    username = form_data.get('username', '')
    new_password = form_data.get('new_password', '')
    confirm_password = form_data.get('confirm_password', '')

    # validating username...
    if not username.strip():
        errors['no_username'] = 'Please enter a username.'

    elif ' ' in username:
        errors['username_spaces'] = 'Username cannot contain spaces'

    if len(username) > 75:
        errors['username_length'] = 'Username is too long.'

    else:
        # checks if username already exists
        sql = "SELECT username FROM Users WHERE username = ?"
        data = (username,)
        user_exists = db.query_all(sql, data)
        if user_exists:
            errors['user_exists'] = "A user with that username already exists."

    # validating passwords...
    if not new_password or not confirm_password:
        errors['no_password'] = 'Please enter a password'
    
    elif new_password != confirm_password:
        errors['new_password'] = 'Passwords do not match'

    elif ' ' in new_password or ' ' in confirm_password:
        errors['password_spaces'] = 'Passwords cannot contain spaces'

    elif len(new_password) > 10000:
        errors['password_length'] = 'Password is a bit too long.'
    return errors

def validate_edit_username_form(form_data):
    """Returns a dictionary of errors (if there are any) associated with the change username form"""

    # Set up errors dictionary
    errors = {}

    # Get the variables
    username = form_data.get('username', '')

    if not username.strip():
        errors['no_username'] = 'Please enter a username.'

    elif ' ' in username:
        errors['username_spaces'] = 'Username cannot contain spaces'

    elif len(username) > 75:
        errors['username_length'] = 'Username must be less than 75 characters.'

    else:
        # checks if username already exists
        sql = "SELECT username FROM Users WHERE username = ? AND user_id != ?"
        data = (username, session['user_id'])
        user_exists = db.query_all(sql, data)
        if user_exists:
            errors['user_exists'] = "A user with that username already exists."

    return errors

def validate_change_password_form(form_data):
    """Returns a dictionary of errors (if there are any) associated with the change username form"""

    # Set up errors dictionary
    errors = {}
    old_password = form_data.get('old_password', '')
    new_password = form_data.get('new_password', '')
    confirm_password = form_data.get('confirm_password', '')

    # validating passwords...
    if not old_password:
        errors['no_old_password'] = 'Please enter in your old password.'

    elif not new_password or not confirm_password:
        errors['no_password'] = 'Please enter a new password'
    
    elif new_password != confirm_password:
        errors['new_password'] = 'Passwords do not match'

    elif ' ' in new_password or ' ' in confirm_password or ' ' in old_password:
        errors['password_spaces'] = 'Passwords cannot contain spaces'

    elif len(new_password) > 75:
        errors['password_length'] = 'Passwords must be less than 75 characters.'

    else:
        # Checks if a user exists (it should), and if the password is correct
        sql = 'SELECT * FROM Users WHERE user_id = ?'
        data = (session['user_id'],)
        user = db.query_one(sql, data)

        if not user:
            abort(401)
        
        elif not check_password_hash(user['password_hash'], old_password):
            errors['old_password'] = 'Password inputted is incorrect'

    return errors
