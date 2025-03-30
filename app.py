from math import e, log
import time
from click import confirm
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import bcrypt
import re
import os
from packages.poker import cards
from packages.poker.gameplay import deal_hands

def is_alphanumeric(s):
    """Check if a string contains only alphanumeric characters."""
    return bool(re.match('^[a-zA-Z0-9]*$', s))

def get_db_connection():
    """Connect to the database."""
    conn = sqlite3.connect("user_data.db")
    conn.row_factory = sqlite3.Row
    return conn

def gbp(value):
    """Format value as GBP."""
    return f"£{value:,.2f}"

def make_tables():
    """Create tables if they do not already exist."""
    try:
        with get_db_connection() as db:
            with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), 'r') as file:
                db.executescript(file.read())
                db.commit()
        db.close()

    except Exception as e:
        print(f"Error during table creation: {e}")

app = Flask(__name__)

app.jinja_env.filters['gbp'] = gbp

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
    user_id = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()['id']
    db.execute("INSERT INTO balance (USER_ID, balance) VALUES (?, ?)", (user_id, 0))
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

@app.route('/game') # TODO: Retrieve player username and balance. Start game
@login_required
def gameplay():
    return render_template('game.html')

@app.route('/game/pre-flop') # TODO: Pre-flop betting
@login_required
def game_pre_flop():
    if 'DECK' not in app.config or app.config['DECK'].size() <= 26:
        app.config['DECK'] = cards.Deck()
        app.config['DECK'].shuffle()
    # Else do nothing bc deck is already shuffled and is big enough

    app.config['PLAYER'] = cards.Player(current_user.username)
    app.config['BOT'] = cards.Player("Bot")

    deal_hands(app.config['DECK'], [app.config['PLAYER'].hand, app.config['BOT'].hand])

    app.config['PLAYER'].hand.display()

    print(app.config['PLAYER'].hand.cards[0])
    print(app.config['PLAYER'].hand.cards[0].__img__())
    print(app.config['PLAYER'].hand.cards[1])
    print(app.config['PLAYER'].hand.cards[1].__img__())

    player_hand = [card.__img__() for card in app.config['PLAYER'].hand.cards]

    table_cards = ['back.png'] * 5

    print(player_hand)

    return render_template('game_pre_flop.html', player_hand=player_hand, table_cards=table_cards, pot_total=0, top_bet=0, current_bet=0, player_balance=0)

@app.route('/game/flop') # TODO: Flop betting
@login_required
def game_flop():
    pass

@app.route('/game/turn') # TODO: Turn betting
@login_required
def game_turn():    
    pass

@app.route('/game/river') # TODO: River betting. Go to result and possibly new/end games
@login_required
def game_river():
    pass

@app.route('/money')
@login_required
def money():
    db = get_db_connection()
    user_id = current_user.id

    transactions_db = db.execute("SELECT * FROM transactions WHERE USER_ID = ?", (user_id,)).fetchall()
    balance_db = db.execute("SELECT balance FROM balance WHERE USER_ID = ?", (user_id,)).fetchone()

    db.close()
    
    balance = balance_db['balance'] if balance_db else 0
    
    return render_template('money.html', transactions=transactions_db, balance=balance)

@app.route('/money/deposit', methods=['POST'])
@login_required
def deposit():
    db = get_db_connection()
    user_id = current_user.id
    amount = request.form['amount']
    db.execute("INSERT INTO transactions (USER_ID, amount) VALUES (?, ?)", (user_id, amount))
    db.execute("UPDATE balance SET balance = balance + ? WHERE USER_ID = ?", (amount, user_id))
    db.commit()
    db.close()
    return redirect(url_for('money'))

@app.route('/money/withdraw', methods=['POST'])
@login_required
def withdraw():
    db = get_db_connection()
    user_id = current_user.id
    try:
        amount = float(request.form['amount'])
        db.execute("INSERT INTO transactions (USER_ID, amount) VALUES (?, ?)", (user_id, -amount))
        db.execute("UPDATE balance SET balance = balance - ? WHERE USER_ID = ?", (amount, user_id))
        db.commit()
    except ValueError:
        flash("Invalid amount entered.", "error")
    finally:
        db.close()
    return redirect(url_for('money'))


if __name__ == '__main__':
    make_tables()
    app.run(debug=True)