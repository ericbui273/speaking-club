import math
import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, request, session, make_response
import config, users, forum

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

@app.route("/")
@app.route("/<int:page>")
def index(page=1):
    page_size = 20
    meetup_count = forum.meetup_count()
    page_count = math.ceil(meetup_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    meetups = forum.get_meetups(page, page_size)
    return render_template("index.html", page=page, page_count=page_count, meetups = meetups)

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

@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    require_login()

    if request.method == "GET":
        return render_template("add_image.html")

    if request.method == "POST":
        file = request.files["image"]
        if not file.filename.endswith(".jpg"):
            return "ERROR: Only .jpg images are allowed!"

        image = file.read()
        if len(image) > 100 * 1024:
            return "ERROR: image is too big!"

        user_id = session["user_id"]
        users.update_image(user_id, image)
        return redirect("/user/" + str(user_id))

@app.route("/image/<int:user_id>")
def show_image(user_id):
    image = users.get_image(user_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response

@app.route("/logout")
def logout():
    require_login()
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
    classes = forum.get_classes(meetup_id)
    return render_template("meetup.html", classes = classes, meetup = meetup, attending_meetups = attending_meetups)

@app.route("/attending/<int:meetup_id>", methods = ["GET","POST"])
def attending(meetup_id):
    require_login()
    meetup = forum.get_meetup(meetup_id)
    if not meetup:
        abort(404)

    if request.method == "GET":
        return render_template("attending.html", meetup = meetup)
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
    require_login()

    if request.method == "GET":
        classes = forum.get_all_classes()
        return render_template("new_post.html", classes=classes)

    title = request.form["title"]
    if not title or len(title) > 100:
        abort(403)
    content = request.form["content"]
    
    date_time = request.form["date_time"]
    venue = request.form["venue"]
    if not date_time or not venue or len(venue) > 100:
        abort(403)

    avail_slot = request.form["avail_slot"]
    host_id = session["user_id"]

    all_classes = forum.get_all_classes()

    classes = []

    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))


    meetup_id = forum.add_meetup(title, date_time, venue, avail_slot, content, host_id, classes)
    return redirect("/meetup/" + str(meetup_id))

@app.route("/edit/<int:meetup_id>", methods=["GET","POST"])
def edit(meetup_id):
    require_login()

    meetup = forum.get_meetup(meetup_id)
    if not meetup:
        abort(404)
    if meetup["host_id"] != session["user_id"]:
        abort(403)

    classes = {}
    all_classes = forum.get_all_classes()
    for my_class in all_classes:
        classes[my_class] = ""
    for entry in forum.get_classes(meetup_id):
        classes[entry["title"]] = entry["value"]

    if request.method == "GET":
        return render_template("edit.html", meetup = meetup, classes=classes, all_classes = forum.get_all_classes())

    title = request.form["title"] 
    if not title or len(title) > 100:
        abort(403)

    date_time = request.form["date_time"] 
    venue = request.form["venue"]
    if not date_time or not venue or len(venue) > 100:
        abort(403)

    avail_slot = int(request.form["avail_slot"])
    if avail_slot:
        if avail_slot < 5 or avail_slot > 50:
            abort(403)
    content = request.form["content"]
    if len(content) > 5000:
        abort(403)

    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes or class_value not in all_classes[class_title]:
                abort(403)
            print(all_classes[class_title])
            classes[class_title] = class_value

    forum.edit_meetup(title, date_time, venue, avail_slot, content, meetup_id,classes)
    return redirect("/meetup/" + str(meetup_id))

@app.route("/remove/<int:meetup_id>", methods = ["GET","POST"])
def remove(meetup_id):
    require_login()

    meetup = forum.get_meetup(meetup_id)
    if not meetup:
        abort(404)

    if meetup["host_id"] != session["user_id"]:
        abort(403)

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

@app.route("/participants/meetup/<int:meetup_id>")
def show_participants(meetup_id):
    require_login()

    meetup = forum.get_meetup(meetup_id)
    if not meetup:
        abort(404)

    participants = forum.get_participants(meetup_id)
    
    if session["user_id"] != meetup["host_id"]:
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

