from click import confirm
from flask import Flask, render_template, request, flash, redirect, url_for
import sqlite3
import bcrypt
import re


def is_alphanumeric(s):
    return bool(re.match('^[a-zA-Z0-9]*$', s))

app = Flask(__name__)
app.secret_key = "b'a\x01\xe0I\x1dB\xd6\x1cGb\xc0:\xe4X\x8fV\xf2\xfb\xb9\xdf\xc0Ld\xbf\x0b<\xf8}-\xa1G\xce'"

def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    return render_template("auth.html")


@app.route('/auth/login', methods=['POST'])
def login():
    # login the reroute to index
    username = request.form['username']
    password = request.form['password']

    db = get_db_connection()
    db_user = db.execute("SELECT password FROM users WHERE username = ?", (username,)).fetchone()
    db.close()

    if db_user is None:
        flash("Invalid username or password", "error")
        return redirect(url_for('auth'))
    
    stored_password = db_user['password']

    if bcrypt.checkpw(password.encode('utf-8'), stored_password):
        return redirect(url_for('index'))
    
    flash("Invalid username or password", "error")
    return redirect(url_for('auth'))


@app.route('/auth/register', methods=['POST'])
def register():
    # register then reroute to login
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']

    if not is_alphanumeric(username):
        flash("Username must be alphanumeric.", "error")
        return redirect(url_for('auth'))
    
    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return redirect(url_for('register'))

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    db = get_db_connection()
    existing_user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    if existing_user:
        flash("Username is already taken.", "error")
        return redirect(url_for('auth'))
    
    db.execute("INSERT INTO users (username, password, first_name, last_name) VALUES (?, ?, ?, ?)", (username, hashed_password, first_name, last_name))
    db.commit()
    db.close()

    flash("Registration successful! Please log in.", "success")
    return redirect(url_for('auth'))
