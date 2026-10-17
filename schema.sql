CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    image BLOB
);

CREATE TABLE meetup (
    id INTEGER PRIMARY KEY,
    title TEXT,
    date_time TEXT,
    venue TEXT,
    avail_slot INTEGER,
    participant_number INTEGER,
    content TEXT,
    host_id INTEGER REFERENCES users
);

CREATE TABLE participants (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    event_id INTEGER REFERENCES meetup,
    participant_name TEXT, 
    language_level TEXT, 
    comment TEXT
);

CREATE TABLE classes(
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE meetup_classes (
    id INTEGER PRIMARY KEY,
    meetup_id INTEGER REFERENCE meetup,
    title TEXT,
    value TEXT
);

CREATE INDEX idx_meetup_participant ON participants (event_id);