CREATE TABLE IF NOT EXISTS mainmenu (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
url text NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
username text NOT NULL,
password text NOT NULL,
admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_topic TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS terms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER,
    term TEXT NOT NULL,
    translation TEXT NOT NULL,
    example TEXT NOT NULL,
    FOREIGN KEY (lesson_id) REFERENCES lessons (id)
);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    u_name TEXT NOT NULL,
    lesson_name TEXT NOT NULL,
    message TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_topic TEXT NOT NULL,
    post_summery TEXT NOT NULL,
    post_oppic BLOB NOT NULL
);

CREATE TABLE IF NOT EXISTS contpost (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_cont TEXT NOT NULL,
    post_pic BLOB,
    post_id INTEGER,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);