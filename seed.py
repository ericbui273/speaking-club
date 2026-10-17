import random, sqlite3
from werkzeug.security import generate_password_hash

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM meetup")
db.execute("DELETE FROM participants")
db.execute("DELETE FROM meetup_classes")

user_count = 100
meetup_count = 10**5
participant_count = 10**6

languages = [
    "Bulgarian",
    "Cantonese",
    "German",
    "Croatian",
    "Swedish",
    "Danish",
    "Dutch",
    "English",
    "Finnish",
    "French"
]

cities = [
    "Espoo",
    "Hämeenlinna",
    "Helsinki",
    "Joensuu",
    "Jyväskylä",
    "Kotka",
    "Kuopio",
    "Kouvola",
    "Lahti",
    "Lappeenranta"
    "Vantaa"
]

levels = [
    "Beginner",
    "Intermediate",
    "Advanced"
]

for i in range(1, user_count + 1):
    #create user with username user+num, password password+num, the password hashing might take a while
    password_hash = generate_password_hash(f"password{i}")
    db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
               ["user" + str(i), password_hash])
#generate meetups
classes = {}
for i in range(1, meetup_count + 1):
    language = random.choice(languages)
    classes["Language"] = language
    city = random.choice(cities)
    classes["City"] = city
    level = random.choice(levels)
    classes["Level"] = level

    title = f"meetup {i} in {language}"
    host_id = random.randint(1, user_count)
    slot = random.randint(5, 50)

    db.execute("""INSERT INTO meetup (id, title, date_time, venue, avail_slot, content, host_id, participant_number) 
                VALUES (?, ?, datetime('now'), ?, ?, ?, ?, 0)""",
               [i, title,  "venue" + str(i), slot, f"Welcome to speak {language}!\nThis meetup is suitable for {level} level.", host_id])

    for val in classes:
        db.execute("""INSERT INTO meetup_classes 
                    (meetup_id, title, value)
                    VALUES (?,?,?)""",
                    [i, val, classes[val]]
        )

for i in range(1, participant_count + 1):
    user_id = random.randint(1, user_count)
    meetup_id = random.randint(1, meetup_count)
    level = random.choice(["Beginner", "Intermediate", "Advanced"])
    db.execute("""INSERT INTO participants (user_id, event_id, participant_name, language_level, comment)
                  VALUES (?, ?, ?, ?, ?)""",
               [user_id, meetup_id, "name" + str(i), level, "no comment"]
    )
    db.execute("""UPDATE meetup 
            SET participant_number = participant_number+1
            WHERE id = ?""",
            [meetup_id]
    )

db.commit()
db.close()