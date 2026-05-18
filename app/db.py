'''
database helper file :)
'''


from app import app
import sqlite3


def get_db():
    """Returns a database connection object"""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db


def edit_db(sql, data=()):
    """Used for INSERT, UPDATE, and DELETE operations"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(sql, data) #I could also write conn.cursor().execute(sql, data)

    conn.commit()
    conn.close()

def query_one(sql, data=()):
    """Returns a single row"""
    conn = get_db()
    cursor = conn.cursor()

    result = cursor.execute(sql, data).fetchone()

    conn.close()
    return result

def query_all(sql, data=()):
    """Returns all cases of the sql"""
    conn = get_db()
    cursor = conn.cursor()

    results = cursor.execute(sql, data).fetchall()

    conn.close()
    return results