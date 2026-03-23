"""Flask web app with session-based auth, Braille conversion, and real-time audio streaming."""

from __future__ import annotations
import subprocess
import os
import re
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import quote

from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_socketio import SocketIO
import PyPDF2
import requests
import AudioBasedStuffs.STTTUTTTS as STTTUTTTS
from AudioBasedStuffs.transliteration import transliterate
from validate_passwd import validate_passwd
from werkzeug.security import check_password_hash, generate_password_hash

# Mapping for English, digits, punctuation, and the base Hebrew consonants -> Unicode Braille.
BRAILLE_MAP = {
    "a": "⠁",
    "b": "⠃",
    "c": "⠉",
    "d": "⠙",
    "e": "⠑",
    "f": "⠋",
    "g": "⠛",
    "h": "⠓",
    "i": "⠊",
    "j": "⠚",
    "k": "⠅",
    "l": "⠇",
    "m": "⠍",
    "n": "⠝",
    "o": "⠕",
    "p": "⠏",
    "q": "⠟",
    "r": "⠗",
    "s": "⠎",
    "t": "⠞",
    "u": "⠥",
    "v": "⠧",
    "w": "⠺",
    "x": "⠭",
    "y": "⠽",
    "z": "⠵",
    "0": "⠚",
    "1": "⠁",
    "2": "⠃",
    "3": "⠉",
    "4": "⠙",
    "5": "⠑",
    "6": "⠋",
    "7": "⠛",
    "8": "⠓",
    "9": "⠊",
    " ": " ",
    "\n": "\n",
    "\t": "\t",
    ".": "⠲",
    ",": "⠂",
    ";": "⠆",
    ":": "⠒",
    "?": "⠦",
    "!": "⠖",
    "'": "⠄",
    '"': "⠶",
    "-": "⠤",
    "/": "⠌",
    "(": "⠐⠣",
    ")": "⠐⠜",
    "#": "⠼",
    "א": "⠁",
    "ב": "⠧",
    "ג": "⠛",
    "ד": "⠙",
    "ה": "⠓",
    "ו": "⠺",
    "ז": "⠵",
    "ח": "⠭",
    "ט": "⠞",
    "י": "⠚",
    "כ": "⠡",
    "ך": "⠡",
    "ל": "⠇",
    "מ": "⠍",
    "ם": "⠍",
    "נ": "⠝",
    "ן": "⠝",
    "ס": "⠎",
    "ע": "⠫",
    "פ": "⠋",
    "ף": "⠋",
    "צ": "⠮",
    "ץ": "⠮",
    "ק": "⠟",
    "ר": "⠗",
    "ש": "⠩",
    "ת": "⠹",
}

#
# Secret key helpers keep Flask sessions stable between restarts.
def _get_secret_file() -> Path:
    """Return the filesystem path where the Flask secret is stored or created."""
    env_path = os.environ.get("VIRTUAL_ENV")
    if env_path:
        return Path(env_path) / "flask_secret_key.txt"
    return Path(__file__).resolve().parent / ".venv" / "flask_secret_key.txt"

#
# Create the secret key file when missing and return the stored value.
def _load_secret_key() -> str:
    """Read the secret key from disk or generate and persist a new one."""
    secret_path = _get_secret_file()
    if secret_path.exists():
        return secret_path.read_text().strip()

    # Ensure the directory exists before persisting the secret key.
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    new_secret = secrets.token_urlsafe(48)
    secret_path.write_text(new_secret)
    try:
        secret_path.chmod(0o600)
    except OSError:
        pass
    return new_secret

#
# Standard Flask + Socket.IO setup using the persistent secret key.
app = Flask(__name__)
app.secret_key = _load_secret_key()
socketio = SocketIO(app, cors_allowed_origins="*")


@dataclass
class User:
    """In-memory user record that stores the normalized username and hashed credential."""
    username: str
    password_hash: str

    def verify_password(self, raw_password: str) -> bool:
        """Return whether the provided password matches this user's hash."""
        return check_password_hash(self.password_hash, raw_password)


# In-memory user registry (clears when the app restarts).
USERS: list[User] = []


#
# Wrap password hashing so registration stays consistent.
def _create_user_entry(username: str, raw_password: str) -> User:
    """Generate a new User instance with a hashed password so the route helpers stay uniform."""
    return User(username=username, password_hash=generate_password_hash(raw_password))


#
# Lookup helper that normalizes the username before searching.
def get_user(username: str) -> Optional[User]:
    """Return the stored User whose normalized username matches the request value."""
    username = username.strip().lower()
    return next((user for user in USERS if user.username.lower() == username), None)


#
# Register a new name once the normalized version is unused.
def register_user(username: str, raw_password: str) -> bool:
    """Add a new account to USERS if the normalized name is still available."""
    if get_user(username):
        return False
    USERS.append(_create_user_entry(username, raw_password))
    return True


#
# Compare hashed credentials and return whether they match.
def authenticate(username: str, raw_password: str) -> bool:
    """Confirm the credentials match a known user."""
    user = get_user(username)
    return bool(user and user.verify_password(raw_password))


#
# Walks the input string and converts each character to a Braille glyph.
def convert_to_braille(text: str) -> str:
    """Translate each character into the configured Braille glyphs, leaving unknowns untouched."""
    return "".join(BRAILLE_MAP.get(char.lower(), char) for char in text)


# Reads text/plain or PDF uploads and returns their extracted text.
def extract_text_from_upload(uploaded_file) -> str:
    """Extract text content from plain text or PDF files submitted via upload."""
    if not uploaded_file or not uploaded_file.filename:
        return ""

    filename = uploaded_file.filename.lower()
    if filename.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")

    if filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(uploaded_file)
        return "".join(page.extract_text() or "" for page in reader.pages)

    return ""


#
# Preconfigured prayers with the label shown and the Sefaria reference used later.
PRAYER_OPTIONS = [
    {
        "label": "Modeh Ani",
        "ref": "Siddur Ashkenaz, Weekday, Shacharit, Preparatory Prayers, Modeh Ani",
    },
    {
        "label": "Shema",
        "ref": "Siddur Ashkenaz, Weekday, Shacharit, Blessings of the Shema, Shema",
    },
    {
        "label": "Amidah",
        "ref": "Siddur Ashkenaz, Weekday, Shacharit, Amidah",
    },
]


#
# Normalize Sefaria HTML responses and split them into cleaned lines.
def clean_sefaria_text(text: str) -> list[str]:
    """Strip HTML tags and collapse whitespace to produce tidy sentence lines."""
    text = text.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    text = re.sub(r"<[^>]+>", "", text)
    lines = []
    for line in text.splitlines():
        cleaned = re.sub(r"\s+", " ", line).strip()
        if cleaned:
            lines.append(cleaned)
    return lines


#
# Recursively flatten nested Sefaria content into a list of strings.
def extract_lines_from_sefaria_content(content) -> list[str]:
    """Walk the mixed data structure returned by Sefaria and gather text lines."""
    if isinstance(content, str):
        return clean_sefaria_text(content)
    if isinstance(content, list):
        lines = []
        for item in content:
            lines.extend(extract_lines_from_sefaria_content(item))
        return lines
    return []


#
# Annotate Hebrew lines with their transliteration for rendering.
def build_transliterated_lines(hebrew_lines: list[str]) -> list[dict[str, str]]:
    """Return dict entries that pair raw Hebrew with its transliteration for templates."""
    return [
        {
            "hebrew": line,
            "transliteration": transliterate(line) or "",
        }
        for line in hebrew_lines
    ]


#
# Fetch prayer text from Sefaria, clean it, and pair each line with transliteration.
def get_prayer_text_from_sefaria(prayer_ref: str) -> list[dict[str, str]]:
    """Call the Sefaria REST API for a prayer ref and prepare the lines for display."""
    encoded_ref = quote(prayer_ref.replace(" ", "_"), safe=",")
    url = f"https://www.sefaria.org/api/texts/{encoded_ref}?context=0"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    hebrew_lines = extract_lines_from_sefaria_content(data.get("he", []))
    return build_transliterated_lines(hebrew_lines)
#
# Seed one default credential so the site has a usable account after startup.
USERS.append(_create_user_entry("Charles", "Charles"))
#
# Utility that flashes a message before redirecting so controllers stay tidy.
def _flash_and_redirect(message: str, category: str, endpoint: str) -> str:
    """Flash a notification and redirect the user to the provided endpoint."""
    flash(message, category)
    return redirect(url_for(endpoint))

#
# Public landing page.
@app.route("/", methods=["GET"])
def index():
    """Render the landing page that prompts visitors to authenticate."""
    return render_template("index.html")


#
# Sign-in form and handler for POSTed credentials.
@app.route("/signin/", methods=["GET", "POST"])
def signin():
    """Handle both rendering the login form and processing POSTed credentials."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        # Validate that the user submitted both fields before checking credentials.

        if not username or not password:
            return _flash_and_redirect("Username and password are required.", "warning", "signin")
        if authenticate(username, password):
            session["username"] = username
            flash("Welcome back!", "success")
            # Charles is treated as admin; everyone else goes to the dashboard.
            if username == "charles":
                return redirect(url_for("admin"))
            return redirect(url_for("dashboard"))

        return _flash_and_redirect("Invalid username or password.", "error", "signin")

    return render_template("signin.html")


#
# Dashboard view requires a logged-in session.
@app.route("/dashboard/")
def dashboard():
    """Show the authenticated dashboard, redirecting unauthenticated users."""
    username = session.get("username")
    # Deny access when no authenticated session exists.
    if not username:
        flash("Please sign in to view your dashboard.", "info")
        return redirect(url_for("signin"))
    return render_template("dashboard.html", username=username)


#
# Registration page that enforces the password policy before storing accounts.
@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Present the account creation form and enforce the password policy."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        # make sure both signup fields were provided.
        if not username or not password:
            return _flash_and_redirect("Username and password are required.", "warning", "signup")

        # Ensure the username is not already registered.
        if get_user(username):
            return _flash_and_redirect("Username already taken.", "error", "signup")

        # Enforce the custom password policy before onboarding.
        if not validate_passwd(password):
            return _flash_and_redirect(
                "Password does not meet the complexity requirements.", "error", "signup"
            )

        register_user(username, password)
        session["username"] = username
        flash("Account created successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("signup.html")


#
# Audio demo page placeholder.
@app.route("/audio/", methods=["GET", "POST"])
def audio():
    return render_template("audio.html")


#
# Braille entry point (reusing the audio template for now).
@app.route("/braille/", methods=["GET", "POST"])
def braille():
    return render_template("audio.html")


#
# Text conversion page that accepts text or file uploads.
@app.route("/texts/", methods=["GET", "POST"])
def texts():
    """Accept text or PDF uploads and convert them into Braille output for the template."""
    braille = None
    if request.method == "POST":
        # Prefer the textarea but fall back to file uploads when empty.
        source_text = request.form.get("text", "").strip()
        if not source_text:
            source_text = extract_text_from_upload(request.files.get("file"))
        if source_text:
            # Convert the gathered source text before presenting it.
            braille = convert_to_braille(source_text)
    return render_template("texts.html", braille=braille)


#
# Prayer-selection page fetching Hebrew text from Sefaria.
@app.route("/tefilla/", methods=["GET", "POST"])
def tefilla():
    """Display prayer reader controls and fetch the selected prayer through Sefaria."""
    selected_prayer = request.args.get("prayer", PRAYER_OPTIONS[0]["ref"])
    if not any(option["ref"] == selected_prayer for option in PRAYER_OPTIONS):
        selected_prayer = PRAYER_OPTIONS[0]["ref"]

    prayer_lines = []
    error_message = None

    try:
        # Attempt to fetch the cleaned lines; handle empty results.
        prayer_lines = get_prayer_text_from_sefaria(selected_prayer)
        if not prayer_lines:
            error_message = "No prayer lines were returned for that selection."
    except requests.RequestException:
        # Surface user-friendly message when Sefaria is unavailable.
        error_message = "Could not load that prayer from Sefaria right now."

    return render_template(
        "tefilla.html",
        prayers=PRAYER_OPTIONS,
        selected_prayer=selected_prayer,
        prayer_lines=prayer_lines,
        error_message=error_message,
    )


#
# Dyslexia help page (static placeholder).
@app.route("/dyslexia/", methods=["GET", "POST"])
def dyslexia():
    """Render the placeholder dyslexia resources view."""
    return render_template("dyslexia.html")


@app.route("/plsnoopenme")
def open_sockets():
    return render_template("openVoiceLine.html")

@app.route("/admin/")
def admin():
    """Render the admin console that lists registered users."""
    return render_template('admin.html')

#
# Removes a user entry from the in-memory store (likely called via admin UI).
@app.route('/delete-user/<username>', methods=['POST'])
def delete_user(username):
    """Remove the named user from the in-memory store and return to admin."""
    # Find the user object and remove it from the global list
    global USERS
    USERS = [user for user in USERS if user.username != username]
    
    # Send the admin back to the list page
    return redirect(url_for('admin_panel'))

def close_previous_sockets():
    blocked_sites=["http://127.0.0.1:5050/"]
    script = 'tell application "Google Chrome" to get URL of tabs of windows'
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    tabs = result.stdout.split(", ")
    for i, tab in enumerate(tabs):
        if any(site in tab for site in blocked_sites):
            close_script = f'tell application "Google Chrome" to close tab {i+1} of window 1'
            subprocess.run(['osascript', '-e', close_script])
#
# Per-client AudioEngine registry keyed by socket session id.
_audio_engines: dict[str, STTTUTTTS.AudioEngine] = {}


@socketio.on("connect")
def handle_connect():
    """Create a dedicated AudioEngine for each connecting client."""
    _audio_engines[request.sid] = STTTUTTTS.create_engine()


@socketio.on("disconnect")
def handle_disconnect():
    """Release the AudioEngine when a client disconnects."""
    _audio_engines.pop(request.sid, None)


#
# SocketIO handler accepts raw audio, transcribes with STTTUTTTS, and broadcasts the transcript.
@socketio.on("audio_stream")
def handle_audio_stream(data):
    # Look up (or lazily create) the per-client engine so recognition state is isolated.
    engine = _audio_engines.get(request.sid)
    if engine is None:
        engine = STTTUTTTS.create_engine()
        _audio_engines[request.sid] = engine

    audio_bytes = bytes(data)
    status, text = engine.process_chunk(audio_bytes)

    if status == "final" and text:
        # Send the recognized transcript back to this client.
        socketio.emit("transcript_result", text, to=request.sid)
        # Dispatch the command to Sefaria and speak the response.
        response = STTTUTTTS.handle_command(text)
        if response:
            speak_text = transliterate(response)
            if speak_text.startswith("Hebrew"):
                speak_text = speak_text[len("Hebrew"):].lstrip(":\n ")
            elif speak_text.startswith("English"):
                speak_text = speak_text[len("English"):].lstrip(":\n ")
            socketio.emit("speak_text", speak_text, to=request.sid)
    elif text:
        # Forward intermediate partial results so the UI stays responsive.
        socketio.emit("partial_result", text, to=request.sid)

def run():
    try:
        socketio.run(app, host="0.0.0.0", port=5050, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"Error: {e}")
        run()
if __name__ == "__main__":
    run()
        
