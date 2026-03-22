"""
Flask web application for user authentication and dashboard access.
Provides routes for sign-in, registration, and a protected dashboard.
"""

from flask import Flask, render_template, url_for, redirect, request, session
from flask_socketio import SocketIO
import PyPDF2
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
app.secret_key = _load_secret_key()

# In-memory user storage for this prototype app.
users = []

# Small starter list of prayer references for the tefilla page dropdown.
# These values are sent directly to the Sefaria API.
PRAYER_OPTIONS = [
    {
        "label": "Modeh Ani",
        "ref": "Siddur Ashkenaz, Weekday, Shacharit, Preparatory Prayers, Modeh Ani"
    },
    {
        "label": "Shema",
        "ref": "Siddur Ashkenaz, Weekday, Shacharit, Blessings of the Shema, Shema"
    },
    {
        "label": "Amidah",
        "ref": "Siddur Ashkenaz, Weekday, Shacharit, Amidah"
    }
]

class User:
    """
    Represents a user with username and password.
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password


def adduser(name, passwd):
    """Create a user object and add it to the in-memory user list."""
    user  = User(name, passwd)
    users.append(user)

# Seed a default user so sign-in works immediately in development.
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
    # Credentials are valid only when both username and password match.
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
    # Walk the user list and return the matching index so other code can reuse it.
    for i in range(len(users)):
        if users[i].username==name:
            return i
    return None


def clean_sefaria_text(text):
    """
    Convert Sefaria HTML into plain readable text while preserving line breaks.

    Args:
        text (str): Raw string returned by the Sefaria API.

    Returns:
        str: Cleaned text with minimal formatting.
    """
    # Treat HTML line breaks like real newlines before stripping the rest of the tags.
    text = re.sub(r"<br\s*/?>", "\n", text)

    # Remove every other HTML tag that may appear in the API response.
    text = re.sub(r"<[^>]+>", "", text)

    # Normalize whitespace inside each line but keep the line structure.
    cleaned_lines = []
    for line in text.splitlines():
        normalized_line = re.sub(r"\s+", " ", line).strip()
        if normalized_line:
            cleaned_lines.append(normalized_line)

    return "\n".join(cleaned_lines)


def extract_lines_from_sefaria_content(content):
    """
    Flatten nested Sefaria content into a simple list of lines.

    Args:
        content (str | list): Hebrew content from the Sefaria API.

    Returns:
        list[str]: Plain-text prayer lines.
    """
    # Strings can be cleaned immediately and split into lines.
    if isinstance(content, str):
        cleaned_text = clean_sefaria_text(content)
        if cleaned_text:
            return cleaned_text.splitlines()
        return []

    # Lists may contain more lists or strings, so recurse through the structure.
    if isinstance(content, list):
        lines = []
        for item in content:
            lines.extend(extract_lines_from_sefaria_content(item))
        return lines

    # Any unsupported type is ignored so the page still renders safely.
    return []


def build_transliterated_lines(hebrew_lines):
    """
    Create a transliterated line for every Hebrew line.

    Args:
        hebrew_lines (list[str]): Clean Hebrew prayer lines.

    Returns:
        list[dict]: Line records used by the tefilla template and JavaScript.
    """
    line_records = []

    # Pair each Hebrew line with a transliterated version so the browser can toggle it.
    for line in hebrew_lines:
        line_records.append(
            {
                "hebrew": line,
                "transliteration": transliterate(line)
            }
        )

    return line_records


def get_prayer_text_from_sefaria(prayer_ref):
    """
    Fetch a prayer from the Sefaria API and return it as line records.

    Args:
        prayer_ref (str): Sefaria text reference selected by the user.

    Returns:
        list[dict]: Prayer lines with Hebrew and transliteration.
    """
    # Sefaria refs work best in URL paths with spaces converted to underscores while
    # keeping commas readable, which matches how Sefaria builds its own text URLs.
    encoded_ref = quote(prayer_ref.replace(" ", "_"), safe=",")
    url = f"https://www.sefaria.org/api/texts/{encoded_ref}?context=0"

    # Ask Sefaria for the prayer text and stop with an error if the request fails.
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    # Read the Hebrew payload and flatten it into plain line-by-line text.
    hebrew_lines = extract_lines_from_sefaria_content(data.get("he", []))

    # Convert those lines into a structure that is easy to use in the template.
    return build_transliterated_lines(hebrew_lines)

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Renders the home page.
    
    Returns:
        str: Rendered HTML template for the index page.
    """
    # The landing page is static, so both GET and POST render the same template.
    return render_template("index.html")

@app.route("/signin/", methods=["GET","POST"])
def signin():
    """
    Handles user sign-in. Validates credentials and redirects accordingly.
    
    Returns:
        str: Rendered signin template or redirect response.
    """
    if request.method == "POST":
        # Read the submitted credentials from the sign-in form.
        usn = request.form["username"]
        passw = request.form["password"]

        # Look up the matching user once, then branch based on the result.
        user_index = find_user(usn)

        if user_index is not None and validate(users[user_index], usn, passw):
            # Store the logged-in username in the session so protected pages can use it.
            session["username"] = usn
            return redirect(url_for("dashboard"))

        elif user_index is not None:
            # Username exists, but the password did not match.
            return "Invalid credentials!"

        else:
            # Unknown users are sent to registration.
            return redirect(url_for("signup"))

    # GET requests simply show the login form.
    return render_template("signin.html")

@app.route("/dashboard/")
def dashboard():
    """
    Renders the dashboard page if user is logged in, otherwise redirects to signin.
    
    Returns:
        str: Rendered dashboard template or redirect response.
    """
    if "username" in session:
        # Pull the username from the session so the template can greet the user.
        username = session.get("username")
        return render_template("dashboard.html", username = username)
    else:
        # Require sign-in before showing the dashboard.
        return redirect(url_for('signin'))

@app.route("/signup/", methods=["GET","POST"])
def signup():
    """
    Handles user signup. Creates a new user if username is available.
    
    Returns:
        str: Rendered signup template or redirect response.
    """
    if request.method == "POST":
        # Capture the new account details from the registration form.
        username = request.form["username"]
        password = request.form["password"]
        # If the username already exists, send the user back to the home page.
        if find_user(username) is not None:
            return redirect(url_for('index'))
        # Otherwise create the account and continue to the dashboard flow.
        adduser(username, password)
        return redirect(url_for('dashboard', username=username))
    # GET requests show the sign-up form.
    return render_template("signup.html")
@app.route("/braille/", methods=["GET","POST"])
def braille():
    """Handle braille route."""
    # This page currently displays static braille-learning resources.
    return render_template("braille.html")

@app.route("/texts/", methods=["GET","POST"])
def texts():
    """Handle texts route."""
    # Start with no Braille output until the user submits text or a file.
    braille = None
    if request.method == "POST":
        # Collect text from either the textarea or an uploaded file.
        text = ""
        if 'text' in request.form:
            text = request.form['text']
        elif 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                filename = file.filename.lower()
                if filename.endswith('.txt'):
                    # Plain text files can be decoded directly.
                    text = file.read().decode('utf-8')
                elif filename.endswith('.pdf'):
                    # PDF files are read page by page and concatenated into one string.
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text()
        if text:
            # Convert each character to Braille when available; leave unknown characters unchanged.
            braille = "".join(braille_map.get(char.lower(), char) for char in text)
    # Render the page with either converted output or an empty result area.
    return render_template("texts.html", braille=braille)

socketio = SocketIO(app, cors_allowed_origins="*")

# --- VOSK SETUP ---
# Ensure your model folder is in the same directory
model = vosk.Model("vosk-model-small-en-us-0.15") 
rec = vosk.KaldiRecognizer(model, 16000)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('audio_stream')
def handle_audio(data):
    """
    This function receives the raw binary bytes from the webpage 
    and passes them directly into Vosk.
    """
    if rec.AcceptWaveform(data):
        # This is a final result (sentence finished)
        result = json.loads(rec.Result())
        print(f"User asked: {result['text']}")
        socketio.emit('transcript_result', result['text'])
    else:
        # This is a partial result (live updates)
        partial = json.loads(rec.PartialResult())
        if partial['partial']:
            print(f"Partial: {partial['partial']}")

@app.route("/tefilla/", methods=["GET","POST"])
def tefilla():
    """Handle tefilla route."""
    # Default to the first prayer in the dropdown the first time the page is opened.
    selected_prayer = request.args.get("prayer", PRAYER_OPTIONS[0]["ref"])

    # Start with empty results so the template can render safely even if the API fails.
    prayer_lines = []
    error_message = None

    try:
        # Fetch the selected prayer from Sefaria and prepare it for playback.
        prayer_lines = get_prayer_text_from_sefaria(selected_prayer)
        if not prayer_lines:
            error_message = "No prayer lines were returned for that selection."
    except Exception:
        # Keep the error simple for the user and avoid crashing the page.
        error_message = "Could not load that prayer from Sefaria right now."

    # Render the page with the dropdown choices and whichever prayer was selected.
    return render_template(
        "tefilla.html",
        prayers=PRAYER_OPTIONS,
        selected_prayer=selected_prayer,
        prayer_lines=prayer_lines,
        error_message=error_message
    )

# Run the development server on port 5050 and expose it to the local network.
app.run(host="0.0.0.0",port=5050)
