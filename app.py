import re
from flask import Flask, render_template, session, redirect, url_for

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key_here'

@app.route('/')
def index():
    return render_template('index.html')
