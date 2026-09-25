CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE meetup (
    id INTEGER PRIMARY KEY,
    title TEXT,
    languages TEXT,
    date_time TEXT,
    venue TEXT,
    avail_slot INTEGER,
    content TEXT,
    host_id INTEGER REFERENCES users
);

CREATE TABLE participants (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    event_id INTEGER REFERENCES meetup
);