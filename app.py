import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, request, session
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

    if not username or not password1 or len(username) not in range(5,51) or len(password1) < 8:
        abort(403)
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
def show_meetup(meetup_id):
    meetup = forum.get_meetup(meetup_id)
    if not meetup:
        abort(404)
    if "user_id" in session:
        attending_meetups = forum.get_attending_meetups(session["user_id"])
    else:
        attending_meetups = []
    return render_template("meetup.html", meetup = meetup, attending_meetups = attending_meetups)

@app.route("/attending/<int:meetup_id>", methods = ["GET","POST"])
def attending(meetup_id):
    if "user_id" not in session:
        abort(403)
    meetup = forum.get_meetup(meetup_id)
    if not meetup:
        abort(404)

    if request.method == "GET":
        return render_template("attending.html", meetup = meetup)
    print(request.form)
    user_id = session["user_id"]
    name = request.form["name"]
    if not name or len(name) > 50:
        abort(403)
    level = request.form["level"] if "level" in request.form else "Unknown"
    if level not in ["Unknown","Beginner", "Intermediate", "Advanced", "Native"]:
        abort(403)

    comment = request.form["comment"] if request.form["comment"] else "No comment"
    if len(comment) > 5000:
        abort(403)

    forum.add_participant(user_id,meetup_id, name, level, comment)
    return redirect("/meetup/" + str(meetup_id))

@app.route("/new_post", methods=["POST", "GET"])
def new_post():
    if "user_id" not in session:
        abort(403)
    if request.method == "GET":
        return render_template("new_post.html")

    title = request.form["title"]
    content = request.form["content"]
    languages = request.form["languages"]
    if not title or not languages or len(languages) > 50 or len(title) > 100 or len(content) > 5000:
        abort(403)
    
    date_time = request.form["date_time"]
    venue = request.form["venue"]
    avail_slot = request.form["avail_slot"]
    
    host_id = session["user_id"]
    meetup_id = forum.add_meetup(title, languages, date_time, venue, avail_slot, content, host_id)
    return redirect("/meetup/" + str(meetup_id))

@app.route("/edit/<int:meetup_id>", methods=["GET","POST"])
def edit(meetup_id):
    if "user_id" not in session:
        abort(403)
    meetup = forum.get_meetup(meetup_id)
    if not meetup:
        abort(404)
    if meetup["host_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("edit.html", meetup = meetup)

    title = request.form["title"] 
    if not title or len(title) > 100:
        abort(403)

    languages = request.form["languages"]
    if not languages or len(languages) > 100:
        abort(403)

    date_time = request.form["date_time"] 
    venue = request.form["venue"] 
    avail_slot = request.form["avail_slot"] 
    content = request.form["content"]
    if len(content) > 5000:
        abort(403)

    forum.edit_meetup(title, languages, date_time, venue, avail_slot, content, meetup_id)
    return redirect("/meetup/" + str(meetup_id))

@app.route("/remove/<int:meetup_id>", methods = ["GET","POST"])
def remove(meetup_id):
    if "user_id" not in session:
        abort(403)

    meetup = forum.get_meetup(meetup_id)
    if not meetup:
        abort(404)

    if meetup["host_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove.html", meetup = meetup)

    if request.method == "POST":
        print(request.method)
        print(request.form)
        if "continue" in request.form:
            forum.remove_meetup(meetup_id)
            return redirect("/")
        return redirect("/meetup/" + str(meetup_id))

@app.route("/search")
def search():
    query = request.args.get("query")
    results = forum.search(query) if query else []
    return render_template("search.html", query=query, results=results)

@app.route("/participants/meetup/<int:meetup_id>")
def show_participants(meetup_id):
    meetup = forum.get_meetup(meetup_id)
    if not meetup:
        abort(404)

    participants = forum.get_participants(meetup_id)
    
    if "user_id" not in session or session["user_id"] != meetup["host_id"]:
        abort(403)

    return render_template("participants.html", meetup=meetup, participants=participants)


@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    host_events = users.get_host_events(user_id)
    attending_events = users.get_attending_events(user_id)
    return render_template("user.html", user = user, host_events = host_events, attending_events=attending_events)

