import math, secrets, sqlite3
from flask import Flask
from flask import make_response, abort, redirect, render_template, request, session, flash
import config, users, forum
import markupsafe

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/")
@app.route("/<int:page>")
def index(page=1):
    page_size = 10
    meetup_count = forum.meetup_count()
    page_count = math.ceil(meetup_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    meetups = forum.get_meetups(page, page_size)

    user = users.get_user(session["user_id"]) if "user_id" in session else None

    return render_template("index.html", user=user, page=page, page_count=page_count, meetups = meetups)

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", filled={})

    username = request.form["username"]
    password1 = request.form["password1"]

    if not username or not password1 or len(username) not in range(5,51) or len(password1) < 8:
        return("Username and password must meet the length requirement!", 403)
    
    password2 = request.form["password2"]
    if password1 != password2:
        flash("ERROR: Passwords don't march!", "error")
        filled = {"username": username}
        return render_template("register.html", filled=filled)

    try:
        users.create_user(username,password1)
        flash("""You have successfully created a new account. 
                Log in now to host and join speaking meetups!""",
                "info"
        )
        return redirect("/")

    except sqlite3.IntegrityError:
        flash("ERROR: username is not available!", "error")
        filled = {"username": username}
        return render_template("register.html", filled=filled)

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "GET":
        return render_template("login.html", filled={}, next_page=request.referrer)

    username = request.form["username"]
    password = request.form["password"]
    next_page = request.form["next_page"]

    user_id = users.check_login(username, password)

    if user_id:
        session["user_id"] = user_id
        session["csrf_token"] = secrets.token_hex(16)
        flash("You are successfully logged in.", "info")
        return redirect(next_page)
    else:
        flash("ERROR: wrong username or password!", "error")
        filled = {"username": username}
        return render_template("login.html", filled=filled, next_page=next_page)

@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    require_login()
    user_id = session["user_id"]
    user = users.get_user(user_id)

    if request.method == "GET":
        return render_template("add_image.html", user=user)

    if request.method == "POST":
        check_csrf()
        file = request.files["image"]
        if not file.filename.endswith(".jpg"):
            flash("ERROR: Only .jpg images are allowed!", "error")
            return render_template("add_image.html", user=user)

        image = file.read()
        if len(image) > 100 * 1024:
            flash("ERROR: image is too big!", "error")
            return render_template("add_image.html")

        users.update_image(user_id, image)
        flash("Updated image successfully", "info")

        return redirect("/user/" + str(user_id))

@app.route("/image/<int:user_id>")
def show_image(user_id):
    image = users.get_image(user_id)
    if not image:
        return("User account does not exist or user does not have any image.", 404)

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
        user = users.get_user(session["user_id"])
    else:
        attending_meetups = []
        user = None

    classes = forum.get_classes(meetup_id)

    return render_template("meetup.html", user=user, classes = classes, meetup = meetup, attending_meetups = attending_meetups)

@app.route("/attending/<int:meetup_id>", methods = ["GET","POST"])
def attending(meetup_id):
    require_login()
    meetup = forum.get_meetup(meetup_id)
    if not meetup:
        abort(404)

    user_id = session["user_id"]
    user = users.get_user(user_id)
    if request.method == "GET":
        return render_template("attending.html", user=user,meetup = meetup)
    
    check_csrf()
    
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
    forum.update_participant_number(meetup_id)
    flash("You have successfully registered to attend this meetup!", "info")
    
    return redirect("/meetup/" + str(meetup_id))

@app.route("/new_post", methods=["POST", "GET"])
def new_post():
    require_login()
    user = users.get_user(session["user_id"])
    if request.method == "GET":
        classes = forum.get_all_classes()
        return render_template("new_post.html", user=user, classes=classes)

    check_csrf()
    title = request.form["title"]
    if not title or len(title) > 100:
        abort(403)
    content = request.form["content"]
    
    request_date_time = request.form["date_time"]
    date_time = request_date_time[:10] + " " + request_date_time[11:]
    venue = request.form["venue"]
    if not date_time or not venue or len(venue) > 100:
        abort(403)

    avail_slot = int(request.form["avail_slot"])
    if avail_slot < 5 or avail_slot > 50:
        abort(403)

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
    
    flash("Meetup created successfully.", "info")
    
    return redirect("/meetup/" + str(meetup_id))

@app.route("/edit/<int:meetup_id>", methods=["GET","POST"])
def edit(meetup_id):
    require_login()
    user = users.get_user(session["user_id"])

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
        return render_template("edit.html", user = user, meetup = meetup, classes=classes, all_classes = forum.get_all_classes())

    check_csrf()
    title = request.form["title"] 
    if not title or len(title) > 100:
        abort(403)

    request_date_time = request.form["date_time"]
    date_time = request_date_time[:10] + " " + request_date_time[11:]

    venue = request.form["venue"]
    if not date_time or not venue or len(venue) > 100:
        abort(403)

    avail_slot = int(request.form["avail_slot"])
    if avail_slot < 5 or avail_slot > 50 or avail_slot < meetup["participant_number"]:
            abort(403)
    content = request.form["content"]
    if len(content) > 5000:
        abort(403)

    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes or class_value not in all_classes[class_title]:
                abort(403)
            classes[class_title] = class_value

    forum.edit_meetup(title, date_time, venue, avail_slot, content, meetup_id,classes)
    flash("Meetup edited successfully.", "info")
    return redirect("/meetup/" + str(meetup_id))

@app.route("/remove/<int:meetup_id>", methods = ["GET","POST"])
def remove(meetup_id):

    require_login()
    user = users.get_user(session["user_id"])

    meetup = forum.get_meetup(meetup_id)
    if not meetup:
        abort(404)

    if meetup["host_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove.html", user = user, meetup = meetup)

    if request.method == "POST":
        check_csrf()
        if "continue" in request.form:
            forum.remove_meetup(meetup_id)
            flash(f"Your meetup {meetup["title"]} has been removed.", "info")
            return redirect("/")
        
        return redirect("/meetup/" + str(meetup_id))

@app.route("/search")
def search():
    query = request.args.get("query")

    page = max(request.args.get("page", type=int, default=1), 1)
    page_size = 10

    results = forum.search(query, page, page_size) if query else []
    result_count = forum.search_result_count(query) if query else None
    
    page_count = max(math.ceil(result_count / page_size), 1) if query else 1
    page = min(page, page_count)
    
    user = users.get_user(session["user_id"]) if "user_id" in session else None
    
    return render_template("search.html", result_count=result_count, page_count=page_count, page=page, user=user,query=query,results=results)

@app.route("/participants/meetup/<int:meetup_id>")
def show_participants(meetup_id):
    require_login()
    user = users.get_user(session["user_id"])

    meetup = forum.get_meetup(meetup_id)
    if not meetup:
        abort(404)

    participants = forum.get_participants(meetup_id)
    
    if session["user_id"] != meetup["host_id"]:
        abort(403)

    return render_template("participants.html", user=user, meetup=meetup, participants=participants)


@app.route("/user/<int:user_id>")
def show_user(user_id):
    shown_user = users.get_user(user_id)

    if not shown_user:
        abort(404)

    host_page = max(request.args.get("host", type=int, default=1), 1)
    attending_page = max(request.args.get("attending", type=int, default=1), 1)
    for value in request.args.keys():
        if value not in ("host", "attending"):
            return (f"Wrong address, '{value}' page does not exist.", 404) 
    
    page_size = 10
    host_count = users.host_event_count(user_id)
    attending_count = users.attending_event_count(user_id)
    host_page_count = max(math.ceil(host_count / page_size), 1)
    attending_page_count = max(math.ceil(attending_count / page_size), 1)

    host_page = min(host_page, host_page_count)
    attending_page = min(attending_page, attending_page_count)

    host_events = users.get_host_events(user_id, host_page, page_size)
    attending_events = users.get_attending_events(user_id, attending_page, page_size)

    user = users.get_user(session["user_id"]) if "user_id" in session else None
    return render_template(
        "user.html", 
        user = user,
        shown_user = shown_user, 
        host_events = host_events, 
        attending_events=attending_events,
        host_count = host_count,
        attending_count = attending_count,
        host_page_count=host_page_count,
        attending_page_count=attending_page_count,
        host_page=host_page,
        attending_page=attending_page
    )
