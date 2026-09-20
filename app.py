import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
import config, users, forum

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "ERROR: Passwords don't march!"

    try:
        users.create_user(username,password1)
        return '<p>Account has been created.</p><p><a href="/login">To the login page</a> <a href="/">To the front page</a></p>'
    except sqlite3.IntegrityError:
        return '<p>ERROR: username is not available!</p><p><a href="/register">Try again</a></p>'

@app.route("/")
def index():
    sessions = forum.get_sessions()
    return render_template("index.html", sessions = sessions) 

@app.route("/session/<int:session_id>")
def show_post(session_id):
    post = forum.get_session(session_id)
    return render_template("session.html", post = post)

@app.route("/new_post", methods=["POST", "GET"])
def new_post():
    if request.method == "GET":
        return render_template("new_post.html")

    title = request.form["title"]
    languages = request.form["languages"]
    date_time = request.form["date_time"]
    venue = request.form["venue"]
    avail_slot = request.form["avail_slot"]
    content = request.form["content"]
    host_id = session["user_id"]
    session_id = forum.add_session(title, languages, date_time, venue, avail_slot, content, host_id)
    return redirect("/session/" + str(session_id))

@app.route("/edit/<int:post_id>", methods=["GET","POST"])
def edit(post_id):
    session = forum.get_session(post_id)
    if request.method == "GET":
        return render_template("edit.html", post = session)

    title = request.form["title"] 
    languages = request.form["languages"] 
    date_time = request.form["date_time"] 
    venue = request.form["venue"] 
    avail_slot = request.form["avail_slot"] 
    content = request.form["content"]
    forum.edit_session(title, languages, date_time, venue, avail_slot, content, post_id)
    return redirect("/session/" + str(post_id))

@app.route("/remove/<int:post_id>", methods = ["GET","POST"])
def remove(post_id):
    session = forum.get_session(post_id)

    if request.method == "GET":
        return render_template("remove.html", post = session)

    if request.method == "POST":
        if "continue" in request.form:
            forum.remove_session(post_id)
            return redirect("/")
        return redirect("/session/" + str(post_id))


@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    user_id = users.check_login(username, password)

    if user_id:
        session["user_id"] = user_id
        return redirect("/")
    else:
        return '<p>ERROR: wrong username or password!</p><p><a href="/login">Try again</a></p>'

@app.route("/logout")
def logout():
    del session["user_id"]
    return redirect("/")