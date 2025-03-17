from math import log
from click import confirm
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import bcrypt
import re


def is_alphanumeric(s):
    return bool(re.match('^[a-zA-Z0-9]*$', s))

def get_db_connection():
    conn = sqlite3.connect("user_data.db")
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)

app.secret_key = "b'a\x01\xe0I\x1dB\xd6\x1cGb\xc0:\xe4X\x8fV\xf2\xfb\xb9\xdf\xc0Ld\xbf\x0b<\xf8}-\xa1G\xce'"
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id, username, first_name):
        self.id = id
        self.username = username
        self.first_name = first_name

@login_manager.user_loader
def load_user(user_id):
    db = get_db_connection()
    user_data = db.execute("SELECT id, username, first_name FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    if user_data:
        return User(id=user_data['id'], username=user_data['username'], first_name=user_data['first_name'])
    return None

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
    db_user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    db.close()

    if db_user is None:
        flash("Invalid username or password", "error")
        return redirect(url_for('auth'))
    
    stored_password = db_user['password']

    if bcrypt.checkpw(password.encode('utf-8'), stored_password):
        user = User(id=db_user['id'], username=db_user['username'], first_name=db_user['first_name'])
        login_user(user)
        return redirect(url_for('home'))
    
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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/game')
@login_required
def game():
    return render_template('game.html')

@app.route('/money')
@login_required
def money():
    return render_template('money.html')
# add tabele for money and implement transactions