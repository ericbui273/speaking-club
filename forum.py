import db

def get_sessions():
    sql = "SELECT * FROM speaking_session"
    return db.query(sql)

def get_session(session_id):
    sql = """SELECT s.*, u.username
            FROM speaking_session AS s, users AS u
            WHERE s.host_id = u.id AND s.id = ?"""
    return db.query(sql,[session_id])[0]

def add_session(title, languages, date_time, venue, avail_slot, content, host_id):
    sql = """INSERT INTO speaking_session (title, languages, date_time, venue, avail_slot, content, host_id) 
            VALUES(?,?,?,?,?,?,?)"""
    db.execute(sql,[title, languages, date_time, venue, avail_slot, content, host_id])
    session_id = db.last_insert_id()
    return session_id

def edit_session(title, languages, date_time, venue, avail_slot, content, id):
    sql = """UPDATE speaking_session
            SET title = ?, languages = ?, date_time = ?, venue = ?, avail_slot = ?, content = ?
            WHERE id = ?"""
    db.execute(sql,[title, languages, date_time, venue, avail_slot, content, id])

def remove_session(session_id):
    sql = "DELETE FROM speaking_session WHERE id = ?"
    db.execute(sql, [session_id])