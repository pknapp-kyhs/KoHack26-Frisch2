"""
Flask web application for user authentication and dashboard access.
Provides routes for sign-in, registration, and a protected dashboard.
"""

from flask import Flask, render_template, url_for, redirect, request, session
import PyPDF2

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

app = Flask(__name__)
# Secret key used by Flask sessions. This is fine for a demo, but it should come
# from a secure environment variable in production.
app.secret_key = "RatherSecretStringHackersPleaseDon'tStealMeI'mTooCoolToStealTrustMe"

# In-memory user storage for this prototype app.
users = []

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

@app.route("/tefilla/", methods=["GET","POST"])
def tefilla():
    """Handle tefilla route."""
    # This route currently serves a placeholder prayer resource page.
    return render_template("tefilla.html")

# Run the development server on port 5050 and expose it to the local network.
app.run(host="0.0.0.0",port=5050)
