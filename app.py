import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
import config, users, forum

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    meetups = forum.get_meetups()
    return render_template("index.html", meetups = meetups) 

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

@app.route("/meetup/<int:meetup_id>")
def show_post(meetup_id):
    meetup = forum.get_meetup(meetup_id)
    return render_template("meetup.html", meetup = meetup)

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
    meetup_id = forum.add_meetup(title, languages, date_time, venue, avail_slot, content, host_id)
    return redirect("/meetup/" + str(meetup_id))

@app.route("/edit/<int:meetup_id>", methods=["GET","POST"])
def edit(meetup_id):
    meetup = forum.get_meetup(meetup_id)

    if request.method == "GET":
        return render_template("edit.html", meetup = meetup)

    title = request.form["title"] 
    languages = request.form["languages"] 
    date_time = request.form["date_time"] 
    venue = request.form["venue"] 
    avail_slot = request.form["avail_slot"] 
    content = request.form["content"]
    forum.edit_meetup(title, languages, date_time, venue, avail_slot, content, meetup_id)
    return redirect("/meetup/" + str(meetup_id))

@app.route("/remove/<int:meetup_id>", methods = ["GET","POST"])
def remove(meetup_id):
    meetup = forum.get_meetup(meetup_id)

    if request.method == "GET":
        return render_template("remove.html", meetup = meetup)

    if request.method == "POST":
        if "continue" in request.form:
            forum.remove_meetup(meetup_id)
            return redirect("/")
        return redirect("/meetup/" + str(meetup_id))

@app.route("/search")
def search():
    query = request.args.get("query")
    results = forum.search(query) if query else []
    return render_template("search.html", query=query, results=results)