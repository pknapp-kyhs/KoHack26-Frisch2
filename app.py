"""Flask web app with session-based auth, Braille conversion, and real-time audio streaming."""

from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_socketio import SocketIO
import PyPDF2
import AudioBasedStuffs.STTTUTTTS as STTTUTTTS
from validate_passwd import validate_passwd
from werkzeug.security import check_password_hash, generate_password_hash

BRAILLE_MAP = {
    'a': 'â ', 'b': 'â ƒ', 'c': 'â ‰', 'd': 'â ™', 'e': 'â ‘', 'f': 'â ‹', 'g': 'â ›', 'h': 'â “',
    'i': 'â Š', 'j': 'â š', 'k': 'â …', 'l': 'â ‡', 'm': 'â ', 'n': 'â ', 'o': 'â •', 'p': 'â ',
    'q': 'â Ÿ', 'r': 'â —', 's': 'â Ž', 't': 'â ž', 'u': 'â ¥', 'v': 'â §', 'w': 'â º', 'x': 'â ­',
    'y': 'â ½', 'z': 'â µ', '×': 'â ', '×‘': 'â ƒ', '×’': 'â ›', '×“': 'â ™', '×”': 'â “',
    '×•': 'â º', '×–': 'â µ', '×—': 'â ¡', '×˜': 'â ž', '×™': 'â Š', '×›': 'â …', '×š': 'â …',
    '×œ': 'â ‡', '×ž': 'â ', '×': 'â ', '× ': 'â ', '×Ÿ': 'â ', '×¡': 'â Ž', '×¢': 'â ¯',
    '×¤': 'â ', '×£': 'â ', '×¦': 'â ¯', '×¥': 'â ¯', '×§': 'â Ÿ', '×¨': 'â —', '×©': 'â ®',
    '×ª': 'â •', ' ': ' ', '.': 'â ²', ',': 'â ‚', '?': 'â ¦', '!': 'â –'
}


def _get_secret_file() -> Path:
    env_path = os.environ.get("VIRTUAL_ENV")
    if env_path:
        return Path(env_path) / "flask_secret_key.txt"
    return Path(__file__).resolve().parent / ".venv" / "flask_secret_key.txt"


def _load_secret_key() -> str:
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
socketio = SocketIO(app, cors_allowed_origins="*")


@dataclass
class User:
    username: str
    password_hash: str

    def verify_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)


USERS: list[User] = []


def _create_user_entry(username: str, raw_password: str) -> User:
    return User(username=username, password_hash=generate_password_hash(raw_password))


def get_user(username: str) -> Optional[User]:
    username = username.strip().lower()
    return next((user for user in USERS if user.username.lower() == username), None)


def register_user(username: str, raw_password: str) -> bool:
    if get_user(username):
        return False
    USERS.append(_create_user_entry(username, raw_password))
    return True


def authenticate(username: str, raw_password: str) -> bool:
    user = get_user(username)
    return bool(user and user.verify_password(raw_password))


def convert_to_braille(text: str) -> str:
    return "".join(BRAILLE_MAP.get(char.lower(), char) for char in text)


def extract_text_from_upload(uploaded_file) -> str:
    if not uploaded_file or not uploaded_file.filename:
        return ""

    filename = uploaded_file.filename.lower()
    if filename.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")

    if filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(uploaded_file)
        return "".join(page.extract_text() or "" for page in reader.pages)

    return ""


USERS.append(_create_user_entry("Charles", "Charles"))


def _flash_and_redirect(message: str, category: str, endpoint: str) -> str:
    flash(message, category)
    return redirect(url_for(endpoint))


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/signin/", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            return _flash_and_redirect("Username and password are required.", "warning", "signin")

        if authenticate(username, password):
            session["username"] = username
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))

        return _flash_and_redirect("Invalid username or password.", "error", "signin")

    return render_template("signin.html")


@app.route("/dashboard/")
def dashboard():
    username = session.get("username")
    if not username:
        flash("Please sign in to view your dashboard.", "info")
        return redirect(url_for("signin"))
    return render_template("dashboard.html", username=username)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            return _flash_and_redirect("Username and password are required.", "warning", "signup")

        if get_user(username):
            return _flash_and_redirect("Username already taken.", "error", "signup")

        if not validate_passwd(password):
            return _flash_and_redirect(
                "Password does not meet the complexity requirements.", "error", "signup"
            )

        register_user(username, password)
        session["username"] = username
        flash("Account created successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("signup.html")


@app.route("/audio/", methods=["GET", "POST"])
def audio():
    return render_template("audio.html")


@app.route("/texts/", methods=["GET", "POST"])
def texts():
    braille = None
    if request.method == "POST":
        source_text = request.form.get("text", "").strip()
        if not source_text:
            source_text = extract_text_from_upload(request.files.get("file"))
        if source_text:
            braille = convert_to_braille(source_text)
    return render_template("texts.html", braille=braille)


@app.route("/tefilla/", methods=["GET", "POST"])
def tefilla():
    return render_template("tefilla.html")


@app.route("/dyslexia/", methods=["GET", "POST"])
def dyslexia():
    return render_template("dyslexia.html")


@app.route("/plsnoopenme")
def open_sockets():
    return render_template("openVoiceLine.html")


@socketio.on("audio_stream")
def handle_audio_stream(data):
    audio_bytes = bytearray(data)
    text = STTTUTTTS.STTTUTTTS(audio_bytes)
    socketio.emit("transcript_result", text)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5050, allow_unsafe_werkzeug=True)
