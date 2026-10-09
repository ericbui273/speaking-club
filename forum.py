import db

def meetup_count():
    return db.query("SELECT COUNT(*) FROM meetup")[0][0]

def get_meetups(page, page_size):
    sql = "SELECT * FROM meetup ORDER BY id LIMIT ? OFFSET ?"

    limit = page_size
    offset = page_size*(page-1)
    return db.query(sql, [limit, offset])

def get_meetup(meetup_id):
    sql = """SELECT m.*, u.username
            FROM meetup AS m, users AS u
            WHERE m.host_id = u.id AND m.id = ?"""
    result = db.query(sql,[meetup_id])
    return result[0] if result else None

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}

    for title, value in result:
        if title not in classes.keys():
            classes[title] = []
        classes[title].append(value)

    return classes

def get_classes(meetup_id):
    sql = "SELECT title, value FROM meetup_classes WHERE meetup_id = ?"
    return db.query(sql, [meetup_id])

def add_meetup(title, date_time, venue, avail_slot, content, host_id, classes):
    sql = """INSERT INTO meetup (title, date_time, venue, avail_slot, content, host_id) 
            VALUES(?,?,?,?,?,?)"""
    db.execute(sql,[title, date_time, venue, avail_slot, content, host_id])
    meetup_id = db.last_insert_id()

    sql2 = "INSERT INTO meetup_classes (meetup_id, title, value) VALUES (?, ?, ?)"
    for i in classes:
        class_title, class_value = i[0], i[1]
        db.execute(sql2, [meetup_id, class_title, class_value])
    print("all classes added (or not)")

    return meetup_id

def edit_meetup(title, date_time, venue, avail_slot, content, id, classes):
    sql = """UPDATE meetup
            SET title = ?, date_time = ?, venue = ?, avail_slot = ?, content = ?
            WHERE id = ?"""
    db.execute(sql,[title, date_time, venue, avail_slot, content, id])

    sql = "DELETE FROM meetup_classes WHERE meetup_id = ?"
    db.execute(sql, [id])

    sql = "INSERT INTO meetup_classes (meetup_id, title, value) VALUES (?, ?, ?)"
    for class_title in classes:
        db.execute(sql, [id, class_title, classes[class_title]])

def remove_meetup(meetup_id):
    sql = "DELETE FROM participants WHERE event_id = ?"
    db.execute(sql, [meetup_id])

    sql = "DELETE FROM meetup WHERE id = ?"
    db.execute(sql, [meetup_id])

    sql = "DELETE FROM meetup_classes WHERE meetup_id = ?"
    db.execute(sql, [meetup_id])

def search(query):
    sql = """SELECT m.*, u.username
            FROM meetup AS m, users AS u
            WHERE m.host_id = u.id AND (m.title LIKE ? OR m.languages LIKE ? OR venue LIKE ? OR content LIKE ? OR u.username LIKE ?)
            ORDER BY m.date_time"""
    return db.query(sql,["%" + query + "%"]*5)

def add_participant(user_id, event_id, name, level, comment):
    sql = """INSERT INTO participants (user_id, event_id, participant_name, language_level, comment)
                VALUES (?,?,?,?,?)"""
    db.execute(sql,[user_id,event_id,name,level,comment])
    participant_id = db.last_insert_id()
    return participant_id

def get_attending_meetups(user_id):
    sql = """SELECT event_id FROM participants
            WHERE user_id = ?"""
    result = db.query(sql,[user_id])
    return [res[0] for res in result] if result else []

def get_participants(meetup_id):
    sql = """SELECT u.username, p.participant_name, p.language_level, p.comment
            FROM participants AS p, users AS u
            WHERE p.user_id = u.id
            AND p.event_id = ?"""
    return db.query(sql,[meetup_id])