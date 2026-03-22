"""
Flask web application for user authentication and dashboard access.
Provides routes for sign-in, registration, and a protected dashboard.
"""

from flask import Flask, render_template, url_for, redirect, request, session


app = Flask(__name__)
# Secret key for session management (should be changed in production)
app.secret_key = "RatherSecretStringHackersPleaseDon'tStealMeI'mTooCoolToStealTrustMe"

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
            return redirect(url_for("register"))

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

@app.route("/register/", methods=["GET","POST"])
def register():
    """
    Handles user registration. Creates a new user if username is available.
    
    Returns:
        str: Rendered register template or redirect response.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if find_user(username) is not None:
            return redirect(url_for('index'))
        adduser(username, password)
        return redirect(url_for('index'))
    return render_template("register.html")


# Run the Flask application on all interfaces at port 5050
app.run(host="0.0.0.0",port=5050)
