import db

def get_meetups():
    sql = "SELECT * FROM meetup"
    return db.query(sql)

def get_meetup(meetup_id):
    sql = """SELECT m.*, u.username
            FROM meetup AS m, users AS u
            WHERE m.host_id = u.id AND m.id = ?"""
    result = db.query(sql,[meetup_id])
    return result[0] if result else None

def add_meetup(title, languages, date_time, venue, avail_slot, content, host_id):
    sql = """INSERT INTO meetup (title, languages, date_time, venue, avail_slot, content, host_id) 
            VALUES(?,?,?,?,?,?,?)"""
    db.execute(sql,[title, languages, date_time, venue, avail_slot, content, host_id])
    meetup_id = db.last_insert_id()
    return meetup_id

def edit_meetup(title, languages, date_time, venue, avail_slot, content, id):
    sql = """UPDATE meetup
            SET title = ?, languages = ?, date_time = ?, venue = ?, avail_slot = ?, content = ?
            WHERE id = ?"""
    db.execute(sql,[title, languages, date_time, venue, avail_slot, content, id])

def remove_meetup(meetup_id):
    sql = "DELETE FROM meetup WHERE id = ?"
    db.execute(sql, [meetup_id])

def search(query):
    sql = """SELECT m.*, u.username
            FROM meetup AS m, users AS u
            WHERE m.host_id = u.id AND (m.title LIKE ? OR m.languages LIKE ? OR venue LIKE ? OR content LIKE ? OR u.username LIKE ?)
            ORDER BY m.date_time"""
    return db.query(sql,["%" + query + "%"]*5)