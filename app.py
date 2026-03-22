from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# TODO Implement this
@app.route('/login/')
def login():
    return render_template('login.html')

# TODO Also implement this
@app.route("/sign-up")
def signup():
    return render_template('sign-up.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')