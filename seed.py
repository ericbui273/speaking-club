import random
import sqlite3

from werkzeug.security import generate_password_hash

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM meetup")
db.execute("DELETE FROM participants")
db.execute("DELETE FROM meetup_classes")

USER_COUNT = 1000
MEETUP_COUNT = 10**5
PARTICIPANT_COUNT = 10**6

LANGUAGES = [
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

CITIES = [
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

LEVELS = [
    "Beginner",
    "Intermediate",
    "Advanced"
]

for i in range(1, USER_COUNT + 1):
    #create user with username = user+num,
    # password = password+num, the password hashing might take a while
    password_hash = generate_password_hash(f"password{i}")
    db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
               ["user" + str(i), password_hash])

#generate meetups
classes = {}
for i in range(1, MEETUP_COUNT + 1):
    language = random.choice(LANGUAGES)
    classes["Language"] = language
    city = random.choice(CITIES)
    classes["City"] = city
    level = random.choice(LEVELS)
    classes["Level"] = level

    title = f"meetup {i} in {language}"
    host_id = random.randint(1, USER_COUNT)
    slot = random.randint(5, 50)
    message = f"Welcome to speak {language}!\nThis meetup is suitable for {level} level."
    db.execute(
        """
        INSERT INTO meetup (
            id,
            title,
            date_time,
            venue,
            avail_slot,
            content,
            host_id,
            participant_number
        )
        VALUES (?, ?, datetime('now'), ?, ?, ?, ?, 0)
        """,
        [i, title, f"venue{str(i)}", slot, message, host_id],
    )

    for val in classes:
        db.execute(
            """
            INSERT INTO meetup_classes (meetup_id, title, value)
            VALUES (?, ?, ?)
            """,
            [i, val, classes[val]],
        )

for i in range(1, PARTICIPANT_COUNT + 1):
    user_id = random.randint(1, USER_COUNT)
    meetup_id = random.randint(1, MEETUP_COUNT)
    level = random.choice(["Beginner", "Intermediate", "Advanced"])

    db.execute(
        """
        INSERT INTO participants (
            user_id,
            event_id,
            participant_name,
            language_level,
            comment
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        [user_id, meetup_id, "name" + str(i), level, "no comment"],
    )

    db.execute(
        """
        UPDATE meetup
        SET participant_number = participant_number + 1
        WHERE id = ?
        """,
        [meetup_id],
    )


db.commit()
db.close()
