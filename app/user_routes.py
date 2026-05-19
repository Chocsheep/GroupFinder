from flask import session, abort, render_template, redirect, url_for, request, flash, current_app
from app import app, db, socketio
from flask_socketio import emit, join_room, leave_room


import os

import app.forms as forms
import app.db as db
from app.db import get_db, query_one, query_all
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid


upload_path = os.path.join(app.root_path, 'static', 'uploads')
if not os.path.exists(upload_path):
    os.makedirs(upload_path)


#? Other functions

def check_login():
    """Redirects with a 401 Not Authorized if the user is not logged in"""
    if 'user_id' not in session:
        abort(401)

def return_username_info():
    """Returns the username info on the edit profile page"""
    sql = 'SELECT username FROM Users WHERE user_id = ?'
    data = (session['user_id'],)
    username = db.query_one(sql, data)['username']
    return username

@app.get('/group/create')
def show_create_group():
    check_login()
    tags = db.query_all('SELECT * FROM Tags')
    print("TAGS:", tags) 
    print("TAGS COUNT:", len(tags)) 
    return render_template('user_pages/create_group.html', tags=tags)

@app.get('/group/<int:group_id>/join')
def join_group(group_id):
    check_login()
    group = db.query_one('SELECT * FROM Groups WHERE groupid = ?', (group_id,))
    members = db.query_all('SELECT * FROM GroupMembers WHERE groupid = ?', (group_id,))
    # Check if room is full
    if group['max_people'] and len(members) >= group['max_people']:
        return redirect(url_for('show_group', group_id=group_id))
    db.edit_db('INSERT OR IGNORE INTO GroupMembers (userid, groupid) VALUES (?, ?)',
               (session['user_id'], group_id))
    return redirect(url_for('show_group', group_id=group_id))

@app.get('/group/<int:group_id>/leave')
def leave_group(group_id):
    check_login()
    db.edit_db('DELETE FROM GroupMembers WHERE userid = ? AND groupid = ?',
               (session['user_id'], group_id))
    # Check if group is now empty, delete if so
    remaining = db.query_all('SELECT * FROM GroupMembers WHERE groupid = ?', (group_id,))
    if len(remaining) == 0:
        db.edit_db('DELETE FROM GroupTags WHERE groupid = ?', (group_id,))
        db.edit_db('DELETE FROM Groups WHERE groupid = ?', (group_id,))
        return redirect(url_for('show_dashboard'))
    return redirect(url_for('show_group', group_id=group_id))

@app.get('/group/<int:group_id>/delete')
def delete_group(group_id):
    check_login()
    group = db.query_one('SELECT * FROM Groups WHERE groupid = ?', (group_id,))
    # Only owner can delete
    if group['owner'] != session['user_id']:
        abort(403)
    db.edit_db('DELETE FROM GroupMembers WHERE groupid = ?', (group_id,))
    db.edit_db('DELETE FROM GroupTags WHERE groupid = ?', (group_id,))
    db.edit_db('DELETE FROM Groups WHERE groupid = ?', (group_id,))
    return redirect(url_for('show_dashboard'))


# secketio stuff for real-time chat :D
@socketio.on('join')
def on_join(data):
    group_id = str(data['group_id'])  # force to string
    join_room(group_id)
    messages = db.query_all('''
        SELECT Messages.content, Messages.created_at, Users.username
        FROM Messages
        JOIN Users ON Messages.userid = Users.userid
        WHERE Messages.groupid = ?
        ORDER BY Messages.created_at ASC
        LIMIT 50
    ''', (group_id,))
    emit('load_messages', [dict(m) for m in messages])

@socketio.on('send_message')
def on_message(data):
    group_id = str(data['group_id'])  # force to string
    content = data['content'].strip()
    if not content:
        return
    db.edit_db(
        'INSERT INTO Messages (groupid, userid, content) VALUES (?, ?, ?)',
        (group_id, session['user_id'], content)
    )
    emit('new_message', {
        'username': session['username'],
        'content': content,
    }, to=group_id)

@app.post('/group/create')
def create_group():
    check_login()

    form_data = dict(request.form)
    name = request.form.get('name')
    description = request.form.get('description')
    location = request.form.get('location')
    max_people = request.form.get('max_people')
    selected_tags = request.form.getlist('tags')
    custom_tag = request.form.get('custom_tag', '').strip()

    if not name:
        return render_template('user_pages/create_group.html',
                               has_creation_error=True,
                               form_data=form_data,
                               tags=db.query_all('SELECT * FROM Tags'))

    # Insert the group
    db.edit_db(
        'INSERT INTO Groups (owner, name, description, location, max_people) VALUES (?, ?, ?, ?, ?)',
        (session['user_id'], name, description, location, max_people or None)
    )

    # Get the new group's id
    new_group = db.query_one(
        'SELECT * FROM Groups WHERE owner = ? ORDER BY groupid DESC',
        (session['user_id'],)
    )
    group_id = new_group['groupid']

    # Add owner as a member
    db.edit_db('INSERT INTO GroupMembers (userid, groupid) VALUES (?, ?)',
               (session['user_id'], group_id))

    # Insert selected tags
    for tag_id in selected_tags:
        db.edit_db('INSERT INTO GroupTags (tagid, groupid) VALUES (?, ?)',
                   (tag_id, group_id))

    # Handle custom tag, create it if it doesn't exist, then link it
    if custom_tag:
        existing = db.query_one('SELECT * FROM Tags WHERE tagname = ?', (custom_tag,))
        if not existing:
            db.edit_db('INSERT INTO Tags (tagname) VALUES (?)', (custom_tag,))
        tag = db.query_one('SELECT * FROM Tags WHERE tagname = ?', (custom_tag,))
        db.edit_db('INSERT OR IGNORE INTO GroupTags (tagid, groupid) VALUES (?, ?)',
                   (tag['tagid'], group_id))

    return redirect(url_for('show_dashboard'))

@app.get('/home')
def show_dashboard():
    check_login()
    
    selected_tags = request.args.getlist('tags')
    
    if selected_tags:
        # Only show groups that have ALL selected tags
        placeholders = ','.join('?' * len(selected_tags))
        groups = db.query_all(f'''
            SELECT Groups.* FROM Groups
            JOIN GroupTags ON Groups.groupid = GroupTags.groupid
            JOIN Tags ON GroupTags.tagid = Tags.tagid
            WHERE Tags.tagname IN ({placeholders})
            GROUP BY Groups.groupid
            HAVING COUNT(DISTINCT Tags.tagid) = ?
        ''', (*selected_tags, len(selected_tags)))
    else:
        groups = db.query_all('SELECT * FROM Groups')
    
    # Tags ordered by number of groups using them
    tags = db.query_all('''
        SELECT Tags.tagname, COUNT(GroupTags.groupid) as group_count
        FROM Tags
        LEFT JOIN GroupTags ON Tags.tagid = GroupTags.tagid
        GROUP BY Tags.tagid
        ORDER BY group_count DESC
    ''')
    
    return render_template('user_pages/dashboard.html', groups=groups, tags=tags, selected_tags=selected_tags)


@app.get('/group/<int:group_id>')
def show_group(group_id):
    check_login()
    group = db.query_one('SELECT * FROM Groups WHERE groupid = ?', (group_id,))
    members = db.query_all('''
        SELECT Users.userid, Users.username, Users.discord
        FROM Users
        JOIN GroupMembers ON Users.userid = GroupMembers.userid
        WHERE GroupMembers.groupid = ?
    ''', (group_id,))
    tags = db.query_all('''
        SELECT Tags.tagname
        FROM Tags
        JOIN GroupTags ON Tags.tagid = GroupTags.tagid
        WHERE GroupTags.groupid = ?
    ''', (group_id,))
    return render_template('user_pages/group_page.html', group=group, members=members, tags=tags)

# delete this later whenever, this is just to check
@app.get('/show_forum')
def show_forum():
    return render_template('user_pages/group_page.html')

@app.get('/show_create_group_form')
def show_create_group_form():
    print("this works")
    return render_template('user_pages/create_group.html')

@app.get('/profile') #show the actual name soon
def show_profile():
    """Shows the users profile"""
    # Checks the user login
    check_login()
    return render_template('user_pages/profile.html')


# we probably dont need this lol
@app.get('/profile/edit') # Shows the edit profile
def show_edit_profile_form():
    """Returns the edit profile form (the settings of the user)"""
    check_login()
    username = return_username_info()

    return render_template('user_pages/edit_profile.html',
                        username=username)

# TEMP: Probably don't need this!
@app.post('/profile/edit/username')
def change_username():
    """Changes the username"""
    check_login()

    # Gets the data and checks if it is valid
    form_data = dict(request.form)
    username_errors = forms.validate_edit_username_form(form_data)

    if username_errors:
        # Repopulates the form if there are issues
        username = return_username_info()
        return render_template('user_pages/edit_profile.html',
                            username=username,
                            username_errors=username_errors,)
    
    else:
        # Changes the username as well as the session, whilst flashing a little message before returning back to the edit profile page.
        username = request.form.get('username')
        sql = 'UPDATE Users SET username = ? WHERE user_id = ?'
        data = (username, session['user_id'])
        db.edit_db(sql, data)
        session['username'] = username

        flash(f"Your username is now changed! It's now '{session['username']}'.")

        return redirect(url_for('show_edit_profile_form'))
    

@app.post('/profile/edit/password')
def change_password():
    """Changes the password"""
    check_login()
    # Gets the data
    form_data = dict(request.form)

    # Checks if something has not been inputted yet, or the passwords don't match
    password_errors = forms.validate_change_password_form(form_data)
    if password_errors:
        # If errors return the other two forms (password will never be filled in, it is not safe that way)
        username = return_username_info()
        return render_template('user_pages/edit_profile.html',
                            username=username,
                            password_errors=password_errors)
    
    else:
        # Gets the password and inputs it into the database.
        password = request.form.get('new_password')
        password_hash = generate_password_hash(password)
        
        sql = """UPDATE Users SET password_hash = ? WHERE user_id = ?"""
        data = (password_hash, session['user_id'])
        db.edit_db(sql, data)

        # Give a little message after editing the database before returning back to the edit profile form.
        flash('Password changed!')
        return redirect(url_for('show_profile'))
    

@app.get('/signout')
def sign_out():
    """Sign the user out and return to the home page"""
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Successfully signed out!')
    return redirect('/')