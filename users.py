from werkzeug.security import check_password_hash, generate_password_hash
import db

def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def check_login(username, password):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])

    if len(result) == 1:
        user_id, password_hash = result[0]
        if check_password_hash(password_hash, password):
            return user_id

    return None

def get_user(user_id):
    sql = """SELECT username, id, image IS NOT NULL as has_image 
            FROM users WHERE id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_host_events(user_id):
    sql = """SELECT id, title, date_time
            FROM meetup
            WHERE host_id = ?"""
    return db.query(sql, [user_id])    

def get_attending_events(user_id):
    sql = """SELECT m.id, m.title, m.date_time, u.username, m.host_id
            FROM meetup AS m, participants AS p, users AS u
            WHERE m.id = p.event_id AND m.host_id = u.id
            AND p.user_id = ?"""
    return db.query(sql,[user_id])

def update_image(user_id, image):
    sql = "UPDATE users SET image = ? WHERE id = ?"
    db.execute(sql, [image, user_id])

def get_image(user_id):
    sql = "SELECT image FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0][0] if result else None