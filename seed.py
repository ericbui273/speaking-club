import random
import sqlite3

import random
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM meetup")
db.execute("DELETE FROM participants")

user_count = 1000
meetup_count = 10**5
participant_count = 10**6

for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username) VALUES (?)",
               ["user" + str(i)])

for i in range(1, meetup_count + 1):
    host_id = random.randint(1, user_count)
    slot = random.randint(5, 50)
    db.execute("""INSERT INTO meetup (title, date_time, venue, avail_slot, content, host_id) 
                VALUES (?, datetime('now'), ?, ?, ?, ?)""",
               ["meetup" + str(i),  "venue" + str(i), slot, "message" + str(i), host_id])

for i in range(1, participant_count + 1):
    user_id = random.randint(1, user_count)
    meetup_id = random.randint(1, meetup_count)
    level = random.choice(["Beginner", "Intermediate", "Advanced"])
    db.execute("""INSERT INTO participants (user_id, event_id, participant_name, language_level, comment)
                  VALUES (?, ?, ?, ?, ?)""",
               [user_id, meetup_id, "name" + str(i), level, "no comment"])

db.commit()
db.close()