from flask import Flask, render_template, url_for, redirect, request, session


app = Flask(__name__)
app.secret_key = "RatherSecretStringHackersPleaseDon'tStealMeI'mTooCoolToStealTrustMe"

users = []

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password


=
charles = User(username="Charles", password="Charles")
users.append(charles)

def validate(user, usn, pw):
    if user.username == usn and user.password == pw:
        return True
    else:
        return False
        
def find_user(name):
    for i in range(len(users)):
        if users[i].username==name:
            return i
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/signin/", methods=["GET","POST"])
def signin():
    if request.method == "POST":
        usn = request.form["username"]
        passw = request.form["password"]

        user_index = find_user(usn)

<<<<<<< HEAD
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
    if "username" in session:
        username = session.get("username")
        return render_template("dashboard.html", username = username)
    else:
        return redirect(url_for('signin'))

@app.route("/register/", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if find_user(username) is not None:
            return redirect(url_for('index'))
        users.append(User(username,password))
        return redirect(url_for('index'))
    return render_template("register.html")


app.run(host="0.0.0.0",port=5050)
=======
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
>>>>>>> 2bfe89d2e8a613f17a6303b8d9323684ebcbeeb7