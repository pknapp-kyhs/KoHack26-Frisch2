"""
Flask web application for user authentication and dashboard access.
Provides routes for sign-in, registration, and a protected dashboard.
"""

from flask import Flask, render_template, url_for, redirect, request, session
from flask_socketio import SocketIO
import PyPDF2
import STTTUTTTS
socketio = SocketIO(app, cors_allowed_origins="*")
# Braille map for English and Hebrew
import re
from urllib.parse import quote
from pathlib import Path
import secrets
import os

import requests

from transliteration import transliterate

# Map supported English/Hebrew characters into Braille symbols for the converter page.
braille_map = {
    # English
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑', 'f': '⠋', 'g': '⠛', 'h': '⠓', 
    'i': '⠊', 'j': '⠚', 'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕', 'p': '⠏', 
    'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞', 'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 
    'y': '⠽', 'z': '⠵',
    # Hebrew
    'א': '⠁', 'ב': '⠃', 'ג': '⠛', 'ד': '⠙', 'ה': '⠓', 'ו': '⠺', 'ז': '⠵', 'ח': '⠡', 
    'ט': '⠞', 'י': '⠊', 'כ': '⠅', 'ך': '⠅', 'ל': '⠇', 'מ': '⠍', 'ם': '⠍', 'נ': '⠝', 
    'ן': '⠝', 'ס': '⠎', 'ע': '⠯', 'פ': '⠏', 'ף': '⠏', 'צ': '⠯', 'ץ': '⠯', 'ק': '⠟', 
    'ר': '⠗', 'ש': '⠮', 'ת': '⠕',
    # Common
    ' ': ' ', '.': '⠲', ',': '⠂', '?': '⠦', '!': '⠖'
}

def _get_secret_file():
    env_path = os.environ.get("VIRTUAL_ENV")
    if env_path:
        venv_path = Path(env_path)
    else:
        venv_path = Path(__file__).resolve().parent / ".venv"
    return venv_path / "flask_secret_key.txt"


def _load_secret_key():
    secret_path = _get_secret_file()
    if secret_path.exists():
        return secret_path.read_text().strip()

    secret_path.parent.mkdir(parents=True, exist_ok=True)
    new_secret = secrets.token_urlsafe(48)
    secret_path.write_text(new_secret)
    try:
        secret_path.chmod(0o600)
    except OSError:
        pass
    return new_secret


app = Flask(__name__)
# Secret key for session management (should be changed in production)
app.secret_key = "RatherSecretStringHackersPleaseDon'tStealMeI'mTooCoolToStealTrustMe"
app.secret_key = _load_secret_key()

# List to store user objects
users = []

class User:
    """
    Represents a user with username and password.
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password


def adduser(name, passwd):
    user  = User(name, passwd)
    users.append(user)

# Create a default user for testing
adduser("Charles", "Charles")

def validate(user, usn, pw):
    """
    Validates if the provided username and password match the user's credentials.
    
    Args:
        user (User): The user object to validate against.
        usn (str): The username to check.
        pw (str): The password to check.
    
    Returns:
        bool: True if credentials match, False otherwise.
    """
    if user.username == usn and user.password == pw:
        return True
    else:
        return False
        
def find_user(name):
    """
    Finds the index of a user in the users list by username.
    
    Args:
        name (str): The username to search for.
    
    Returns:
        int or None: The index of the user if found, None otherwise.
    """
    for i in range(len(users)):
        if users[i].username==name:
            return i
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Renders the home page.
    
    Returns:
        str: Rendered HTML template for the index page.
    """
    return render_template("index.html")

@app.route("/signin/", methods=["GET","POST"])
def signin():
    """
    Handles user sign-in. Validates credentials and redirects accordingly.
    
    Returns:
        str: Rendered signin template or redirect response.
    """
    if request.method == "POST":
        usn = request.form["username"]
        passw = request.form["password"]

        user_index = find_user(usn)

        if user_index is not None and validate(users[user_index], usn, passw):
            session["username"] = usn
            return redirect(url_for("dashboard"))

        elif user_index is not None:
            return "Invalid credentials!"

        else:
            return redirect(url_for("signup"))

    return render_template("signin.html")

@app.route("/dashboard/")
def dashboard():
    """
    Renders the dashboard page if user is logged in, otherwise redirects to signin.
    
    Returns:
        str: Rendered dashboard template or redirect response.
    """
    if "username" in session:
        username = session.get("username")
        return render_template("dashboard.html", username = username)
    else:
        return redirect(url_for('signin'))

@app.route("/signup/", methods=["GET","POST"])
def signup():
    """
    Handles user signup. Creates a new user if username is available.
    
    Returns:
        str: Rendered signup template or redirect response.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if find_user(username) is not None:
            return redirect(url_for('index'))
        adduser(username, password)
        return redirect(url_for('dashboard', username=username))
    return render_template("signup.html")
@app.route("/braille/", methods=["GET","POST"])
def braille():
    """Handle braille route."""
    return render_template("braille.html")

@app.route("/texts/", methods=["GET","POST"])
def texts():
    """Handle texts route."""
    braille = None
    if request.method == "POST":
        text = ""
        if 'text' in request.form:
            text = request.form['text']
        elif 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                filename = file.filename.lower()
                if filename.endswith('.txt'):
                    text = file.read().decode('utf-8')
                elif filename.endswith('.pdf'):
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text()
        if text:
            braille = "".join(braille_map.get(char.lower(), char) for char in text)
    return render_template("texts.html", braille=braille)



@app.route("/tefilla/", methods=["GET","POST"])
def tefilla():
    """Handle tefilla route."""
    return render_template("tefilla.html")

@app.route("/dyslexia/", methods=["GET","POST"])
def dyslexia():
    """Handle dyslexia route."""
    return render_template("dyslexia.html")

@app.route("plsnoopenme")
def openSockets():
    return render_template('openVoiceLine.html')

# @socketio.on('audio_stream')
# def handle_audio(data):
#     STTTUTTTS.STTTUTTTS()
#     return 
# Run the Flask application on all interfaces at port 5050
app.run(host="0.0.0.0",port=5050)
