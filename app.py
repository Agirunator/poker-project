import random
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
import sqlite3
import bcrypt
import re
import os
from packages.poker import cards, eval
from packages.poker.gameplay import deal_hands


def is_alphanumeric(s):
    """Check if a string contains only alphanumeric characters."""
    return bool(re.match("^[a-zA-Z0-9]*$", s))


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
            with open(
                os.path.join(os.path.dirname(__file__), "schema.sql"), "r"
            ) as file:
                db.executescript(file.read())
                db.commit()
        db.close()

    except Exception as e:
        print(f"Error during table creation: {e}")


app = Flask(__name__)

app.jinja_env.filters["gbp"] = gbp

app.secret_key = os.urandom(32)
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
    user_data = db.execute(
        "SELECT id, username, first_name FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    db.close()
    if user_data:
        return User(
            id=user_data["id"],
            username=user_data["username"],
            first_name=user_data["first_name"],
        )
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/auth", methods=["GET", "POST"])
def auth():
    return render_template("auth.html")


@app.route("/auth/login", methods=["POST"])
def login():
    # login the reroute to index
    username = request.form["username"]
    password = request.form["password"]

    db = get_db_connection()
    db_user = db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    db.close()

    if db_user is None:
        flash("Invalid username or password", "error")
        return redirect(url_for("auth"))

    stored_password = db_user["password"]

    if bcrypt.checkpw(password.encode("utf-8"), stored_password):
        user = User(
            id=db_user["id"],
            username=db_user["username"],
            first_name=db_user["first_name"],
        )
        login_user(user)
        return redirect(url_for("home"))

    flash("Invalid username or password", "error")
    return redirect(url_for("auth"))


@app.route("/auth/register", methods=["POST"])
def register():
    # register then reroute to login
    username = request.form["username"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]

    if not is_alphanumeric(username):
        flash("Username must be alphanumeric.", "error")
        return redirect(url_for("auth"))

    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return redirect(url_for("register"))

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    db = get_db_connection()
    existing_user = db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()

    if existing_user:
        flash("Username is already taken.", "error")
        return redirect(url_for("auth"))

    db.execute(
        "INSERT INTO users (username, password, first_name, last_name) VALUES (?, ?, ?, ?)",
        (username, hashed_password, first_name, last_name),
    )
    db.commit()
    user_id = db.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()["id"]
    db.execute("INSERT INTO balance (USER_ID, balance) VALUES (?, ?)", (user_id, 0))
    db.commit()
    db.close()

    flash("Registration successful! Please log in.", "success")
    return redirect(url_for("auth"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/home")
@login_required
def home():
    return render_template("home.html")


@app.route("/rules")
def rules():
    return render_template("rules.html")


@app.route("/game")  # TODO: Retrieve player username and balance. Start game
@login_required
def game():
    return render_template("game.html")


@app.route("/game/start", methods=["POST"])
@login_required
def start_game():
    db = get_db_connection()
    user_id = current_user.id
    balance_db = db.execute(
        "SELECT balance FROM balance WHERE USER_ID = ?", (user_id,)
    ).fetchone()
    db.close()
    if balance_db["balance"] < 5:
        flash("You don't have enough money to play", "error")
        return redirect(url_for("money"))

    if "DECK" not in app.config or app.config["DECK"].size() <= 26:
        app.config["DECK"] = cards.Deck()
        app.config["DECK"].shuffle()
    # Else do nothing bc deck is already shuffled and is big enough

    # if "PLAYER_START" not in app.config:
    #     app.config["PLAYER_START"] = True

    # if app.config["PLAYER_START"]:
    #     app.config["PLAYER_TURN"] = True
    # else:
    #     app.config["PLAYER_TURN"] = False

    app.config["PLAYER_TURN"] = True

    app.config["PLAYER"] = cards.Player(current_user.username)
    app.config["BOT"] = cards.Player("Bot")

    app.config["TABLE"] = cards.Table()

    app.config["ROUND"] = 0

    db = get_db_connection()
    user_id = current_user.id
    db.execute("UPDATE balance SET balance = balance - 5 WHERE USER_ID = ?", (user_id,))
    db.commit()
    db.execute(
        "INSERT INTO transactions (USER_ID, amount) VALUES (?, ?)", (user_id, -5)
    )
    db.commit()
    db.close()

    app.config["PLAYER"].place_bet(5)
    app.config["BOT"].place_bet(5)

    return redirect(url_for("play_game"))


@app.route("/game/play", methods=["GET", "POST"])
@login_required
def play_game():
    if app.config["PLAYER_TURN"]:
        db = get_db_connection()
        balance_db = db.execute(
            "SELECT * FROM balance WHERE USER_ID = ?", (current_user.id,)
        ).fetchone()
        db.close()
        match app.config["ROUND"]:
            # TODO render templates
            case 0:
                # Pre-flop
                if app.config["PLAYER"].hand.size() == 0:
                    deal_hands(
                        app.config["DECK"],
                        [app.config["PLAYER"].hand, app.config["BOT"].hand],
                    )
                return render_template(
                    "game_pre_flop.html",  #! need to make this
                    player_hand=[
                        card.__img__() for card in app.config["PLAYER"].hand.cards
                    ],
                    pot_total=app.config["PLAYER"].bet + app.config["BOT"].bet,
                    player_balance=balance_db["balance"],
                    current_bet=app.config["PLAYER"].bet,
                )
            case 1:
                # Flop
                if len(app.config["TABLE"].flop) == 0:
                    app.config["DECK"].deal()  # burn card
                    app.config["TABLE"].deal_flop(app.config["DECK"])
                return render_template(
                    "game_flop.html",  #! need to make this
                    flop=[card.__img__() for card in app.config["TABLE"].flop],
                    player_hand=[
                        card.__img__() for card in app.config["PLAYER"].hand.cards
                    ],
                    pot_total=app.config["PLAYER"].bet + app.config["BOT"].bet,
                    player_balance=balance_db["balance"],
                    current_bet=app.config["PLAYER"].bet,
                )
            case 2:
                # Turn
                if len(app.config["TABLE"].turn) == 0:
                    app.config["DECK"].deal()  # burn card
                    app.config["TABLE"].deal_turn(app.config["DECK"])
                return render_template(
                    "game_turn.html",  #! need to make this
                    flop=[card.__img__() for card in app.config["TABLE"].flop],
                    turn=[card.__img__() for card in app.config["TABLE"].turn],
                    player_hand=[
                        card.__img__() for card in app.config["PLAYER"].hand.cards
                    ],
                    pot_total=app.config["PLAYER"].bet + app.config["BOT"].bet,
                    player_balance=balance_db["balance"],
                    current_bet=app.config["PLAYER"].bet,
                )
            case 3:
                # River
                if len(app.config["TABLE"].river) == 0:
                    app.config["DECK"].deal()  # burn card
                    app.config["TABLE"].deal_river(app.config["DECK"])
                return render_template(
                    "game_river.html",  #! need to make this
                    flop=[card.__img__() for card in app.config["TABLE"].flop],
                    turn=[card.__img__() for card in app.config["TABLE"].turn],
                    river=[card.__img__() for card in app.config["TABLE"].river],
                    player_hand=[
                        card.__img__() for card in app.config["PLAYER"].hand.cards
                    ],
                    pot_total=app.config["PLAYER"].bet + app.config["BOT"].bet,
                    player_balance=balance_db["balance"],
                    current_bet=app.config["PLAYER"].bet,
                )
    else:
        return redirect(url_for("game_bot_turn"))


@app.route("/game/bet", methods=["POST"])
@login_required
def game_bet():
    bet_amount = request.form.get("bet_amount", "").strip()

    # Check if the bet_amount is not empty and is a valid number
    if bet_amount and bet_amount.isdigit():
        bet_amount = float(bet_amount)
    else:
        bet_amount = 0.0

    match request.form["action"]:
        case "check":
            if app.config["PLAYER"].bet < app.config["BOT"].bet:
                flash("You cannot check, you must call or raise.", "info")
            else:
                flash(f'{app.config["PLAYER"].name} checks.', "info")
        case "call":
            if app.config["PLAYER"].bet >= app.config["BOT"].bet:
                flash("You cannot call, you must check or raise.", "info")
            else:
                call_amount = app.config["BOT"].bet - app.config["PLAYER"].bet
                db = get_db_connection()
                user_id = current_user.id
                db.execute(
                    "UPDATE balance SET balance = balance - ? WHERE USER_ID = ?",
                    (call_amount, user_id),
                )
                db.commit()
                db.execute(
                    "INSERT INTO transactions (USER_ID, amount) VALUES (?, ?)",
                    (user_id, -call_amount),
                )
                db.commit()
                db.close()
                app.config["PLAYER"].place_bet(call_amount)
                flash(f'{app.config["PLAYER"].name} calls {call_amount}.', "info")
        case "fold":
            app.config["PLAYER"].fold()
            flash(f'{app.config["PLAYER"].name} folds.', "info")
            return redirect(url_for("end_game"))
        case "raise":
            if bet_amount <= app.config["BOT"].bet - app.config["PLAYER"].bet:
                flash(
                    f'Your raise must be greater than {app.config["BOT"].bet - app.config["PLAYER"].bet}.',
                    "info",
                )
            else:
                db = get_db_connection()
                user_id = current_user.id
                db.execute(
                    "UPDATE balance SET balance = balance - ? WHERE USER_ID = ?",
                    (bet_amount, user_id),
                )
                db.commit()
                db.execute(
                    "INSERT INTO transactions (USER_ID, amount) VALUES (?, ?)",
                    (user_id, -bet_amount),
                )
                db.commit()
                db.close()
                app.config["PLAYER"].place_bet(bet_amount)
                flash(f'{app.config["PLAYER"].name} raises {bet_amount}.', "info")

    app.config["PLAYER_TURN"] = False

    return redirect(url_for("play_game"))


@app.route("/game/bot_turn")
@login_required
def game_bot_turn():
    # player either bet increases or stays the same
    if app.config["BOT"].bet < app.config["PLAYER"].bet:
        # bot calls or raises or folds
        actions = ["call", "raise", "fold"]
        action_probabilities = [0.8, 0.15, 0.05]
        bot_action = random.choices(actions, action_probabilities)[0]
        match bot_action:
            case "call":
                call_amount = app.config["PLAYER"].bet - app.config["BOT"].bet
                app.config["BOT"].place_bet(call_amount)
                flash(f"Bot calls {call_amount}.", "info")
            case "raise":
                db = get_db_connection()
                user_id = current_user.id
                balance_db = db.execute(
                    "SELECT balance FROM balance WHERE USER_ID = ?", (user_id,)
                ).fetchone()
                user_balance = balance_db["balance"]
                db.close()

                raise_amounts = [
                    5 if 5 <= user_balance else user_balance,
                    10 if 10 <= user_balance else user_balance,
                    20 if 20 <= user_balance else user_balance,
                    100 if 100 <= user_balance else user_balance,
                ]
                raise_probabilities = [0.5, 0.3, 0.19, 0.01]
                bot_raise_amount = random.choices(raise_amounts, raise_probabilities)[0]
                app.config["BOT"].place_bet(bot_raise_amount)
                flash(f"Bot raises by {bot_raise_amount}.", "info")
            case "fold":
                app.config["BOT"].fold()
                flash("Bot folds.", "info")
                return redirect(url_for("end_game"))
    else:
        # bot checks or raises
        actions = ["check", "raise"]
        action_probabilities = [0.8, 0.2]
        bot_action = random.choices(actions, action_probabilities)[0]
        match bot_action:
            case "check":
                flash("Bot checks.", "info")
                pass
            case "raise":
                db = get_db_connection()
                user_id = current_user.id
                balance_db = db.execute(
                    "SELECT balance FROM balance WHERE USER_ID = ?", (user_id,)
                ).fetchone()
                user_balance = balance_db["balance"]
                db.close()

                raise_amounts = [
                    5 if 5 <= user_balance else user_balance,
                    10 if 10 <= user_balance else user_balance,
                    20 if 20 <= user_balance else user_balance,
                    100 if 100 <= user_balance else user_balance,
                ]
                raise_probabilities = [0.5, 0.3, 0.19, 0.01]
                bot_raise_amount = random.choices(raise_amounts, raise_probabilities)[0]
                app.config["BOT"].place_bet(bot_raise_amount)
                flash(f"Bot raises by {bot_raise_amount}.", "info")

    if app.config["PLAYER"].bet == app.config["BOT"].bet:
        app.config["ROUND"] += 1
        if app.config["ROUND"] > 3:
            return redirect(url_for("end_game"))
        flash("Both bets are equal. Proceeding to the next round.", "info")
    app.config["PLAYER_TURN"] = True
    return redirect(url_for("play_game"))


#! Display both hands on this route and give options for home or new game
@app.route("/game/end")
@login_required
def end_game():
    player_best = eval.best_hand(app.config["PLAYER"].hand, app.config["TABLE"])
    bot_best = eval.best_hand(app.config["BOT"].hand, app.config["TABLE"])

    if not app.config["PLAYER"].hand:
        flash("Bot wins!", "info")
        db = get_db_connection()
        user_id = current_user.id
        balance_db = db.execute(
            "SELECT balance FROM balance WHERE USER_ID = ?", (user_id,)
        ).fetchone()
        db.close()
        return render_template(
            "game_end_fold.html",
            player_hand=[card.__img__() for card in app.config["PLAYER"].hand.cards],
            flop=[card.__img__() for card in app.config["TABLE"].flop],
            turn=[card.__img__() for card in app.config["TABLE"].turn],
            river=[card.__img__() for card in app.config["TABLE"].river],
            pot_total=app.config["PLAYER"].bet + app.config["BOT"].bet,
            player_balance=balance_db["balance"],
        )  # TODO: html page

    if not app.config["BOT"].hand:
        flash("Player wins!", "info")
        winnings = app.config["PLAYER"].bet + app.config["BOT"].bet
        db = get_db_connection()
        user_id = current_user.id
        db.execute(
            "UPDATE balance SET balance = balance + ? WHERE USER_ID = ?",
            (winnings, user_id),
        )
        db.commit()
        db.execute(
            "INSERT INTO transactions (USER_ID, amount) VALUES (?, ?)",
            (user_id, winnings),
        )
        db.commit()
        db.close()
        db = get_db_connection()
        user_id = current_user.id
        balance_db = db.execute(
            "SELECT balance FROM balance WHERE USER_ID = ?", (user_id,)
        ).fetchone()
        db.close()
        return render_template(
            "game_end_fold.html",
            player_hand=[card.__img__() for card in app.config["PLAYER"].hand.cards],
            flop=[card.__img__() for card in app.config["TABLE"].flop],
            turn=[card.__img__() for card in app.config["TABLE"].turn],
            river=[card.__img__() for card in app.config["TABLE"].river],
            pot_total=app.config["PLAYER"].bet + app.config["BOT"].bet,
            player_balance=balance_db["balance"],
        )  # TODO: html page

    if player_best["hand_rank"] > bot_best["hand_rank"]:
        flash("Player wins!", "info")
        winnings = app.config["PLAYER"].bet + app.config["BOT"].bet
        db = get_db_connection()
        user_id = current_user.id
        db.execute(
            "UPDATE balance SET balance = balance + ? WHERE USER_ID = ?",
            (winnings, user_id),
        )
        db.commit()
        db.execute(
            "INSERT INTO transactions (USER_ID, amount) VALUES (?, ?)",
            (user_id, winnings),
        )
        db.commit()
        db.close()
    elif player_best["hand_rank"] < bot_best["hand_rank"]:
        flash("Bot wins!", "info")
    else:
        flash("It's a tie!", "info")
        db = get_db_connection()
        user_id = current_user.id
        db.execute(
            "UPDATE balance SET balance = balance + ? WHERE USER_ID = ?",
            (app.config["PLAYER"].bet, user_id),
        )
        db.commit()
        db.execute(
            "INSERT INTO transactions (USER_ID, amount) VALUES (?, ?)",
            (user_id, app.config["PLAYER"].bet),
        )
        db.commit()
        db.close()

    db = get_db_connection()
    balance_db = db.execute(
        "SELECT balance FROM balance WHERE USER_ID = ?", (current_user.id,)
    ).fetchone()
    db.close()

    return render_template(  # TODO: html page
        "game_end.html",
        flop=[card.__img__() for card in app.config["TABLE"].flop],
        turn=[card.__img__() for card in app.config["TABLE"].turn],
        river=[card.__img__() for card in app.config["TABLE"].river],
        player_hand=[card.__img__() for card in app.config["PLAYER"].hand.cards],
        bot_hand=[card.__img__() for card in app.config["BOT"].hand.cards],
        pot_total=app.config["PLAYER"].bet + app.config["BOT"].bet,
        player_balance=balance_db["balance"],
    )


@app.route("/money")
@login_required
def money():
    db = get_db_connection()
    user_id = current_user.id

    transactions_db = db.execute(
        "SELECT * FROM transactions WHERE USER_ID = ?", (user_id,)
    ).fetchall()
    balance_db = db.execute(
        "SELECT balance FROM balance WHERE USER_ID = ?", (user_id,)
    ).fetchone()

    db.close()

    balance = balance_db["balance"] if balance_db else 0

    return render_template("money.html", transactions=transactions_db, balance=balance)


@app.route("/money/deposit", methods=["POST"])
@login_required
def deposit():
    db = get_db_connection()
    user_id = current_user.id
    amount = request.form["amount"]
    db.execute(
        "INSERT INTO transactions (USER_ID, amount) VALUES (?, ?)", (user_id, amount)
    )
    db.commit()
    db.execute(
        "UPDATE balance SET balance = balance + ? WHERE USER_ID = ?", (amount, user_id)
    )
    db.commit()
    db.close()
    return redirect(url_for("money"))


@app.route("/money/withdraw", methods=["POST"])
@login_required
def withdraw():
    db = get_db_connection()
    user_id = current_user.id
    try:
        amount = float(request.form["amount"])
        db.execute(
            "INSERT INTO transactions (USER_ID, amount) VALUES (?, ?)",
            (user_id, -amount),
        )
        db.commit()
        db.execute(
            "UPDATE balance SET balance = balance - ? WHERE USER_ID = ?",
            (amount, user_id),
        )
        db.commit()
    except ValueError:
        flash("Invalid amount entered.", "error")
    finally:
        db.close()
    return redirect(url_for("money"))


if __name__ == "__main__":
    make_tables()
    app.run(debug=True)
