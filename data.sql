-- $ sqlite3 data.db < data.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS votes;
DROP TABLE IF EXISTS community;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS favorite;

CREATE TABLE community (
    community_id INTEGER PRIMARY KEY,
    community_name VARCHAR NOT NULL
);

CREATE TABLE votes (
    vote_id INTEGER primary key,
    upvotes INTEGER NOT NULL,
    downvotes INTEGER NOT NULL
);

CREATE TABLE posts (
    post_id INTEGER PRIMARY KEY,
    community_id INTEGER NOT NULL,
    title VARCHAR NOT NULL,
    description VARCHAR,
    resource_url VARCHAR,
    published TIMESTAMP DEFAULT (DATETIME('now', 'localtime')),
    username VARCHAR NOT NULL,
    vote_id INTEGER NOT NULL,
    FOREIGN KEY (vote_id) REFERENCES votes (vote_id),
    FOREIGN KEY (community_id) REFERENCES community (community_id)
);

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    karma INTEGER DEFAULT 1
);

CREATE TABLE messages (
    msg_id INTEGER PRIMARY KEY,
    user_from INTEGER NOT NULL,
    user_to INTEGER NOT NULL,
    msg_time TIMESTAMP DEFAULT (DATETIME('now', 'localtime')),
    msg_content VARCHAR NOT NULl,
    msg_flag VARCHAR,
    FOREIGN KEY (user_from) REFERENCES users (user_id),
    FOREIGN KEY (user_to) REFERENCES users (user_id)
);

CREATE TABLE favorite (
    fav_id INTEGER PRIMARY KEY,
    msg_ID INTEGER NOT NULL,
    FOREIGN KEY (msg_ID) REFERENCES messages (msg_id)
);

INSERT INTO users(username, email) VALUES ('ilovedog', 'dogperson@ilovedog.com');
INSERT INTO users(username, email) VALUES ('ilovecat', 'catperson@ilovecat.com');

INSERT INTO messages(user_from, user_to, msg_content, msg_flag)
        VALUES (1, 2, 'hey friend', 'important');

INSERT INTO favorite(msg_ID) VALUES (1);
INSERT INTO favorite(msg_ID) VALUES (2);

INSERT INTO votes(upvotes, downvotes) VALUES(103, 24);
INSERT INTO community(community_id, community_name) VALUES(1, 'cheesecake');
INSERT INTO posts(community_id, title, description, resource_url, username, vote_id)
VALUES(
    (SELECT community_id FROM community WHERE community_name='cheesecake'),
    'The Best Cheesecake Recipe',
    'This was too good, you have to try it.',
    'https://sugarspunrun.com/best-cheesecake-recipe/',
    'cakeLvr',
    (SELECT MAX(vote_id) from votes)
);

INSERT INTO votes(upvotes, downvotes) VALUES(64, 0);
INSERT INTO community(community_id, community_name) VALUES(2, 'coronavirus');
INSERT INTO posts(community_id, title, description, username, vote_id)
VALUES(
    (SELECT community_id FROM community WHERE community_name='coronavirus'),
    'Best defence against coronavirus',
    'Wash your hands!',
    'healthLvr',
    (SELECT MAX(vote_id) from votes)
);

INSERT INTO votes(upvotes, downvotes) VALUES(78, 16);
INSERT INTO posts(community_id, title, description, resource_url, username, vote_id)
VALUES(
    (SELECT community_id FROM community WHERE community_name='coronavirus'),
    '100 things to do in quarantine',
    'I have already done 99 of them.',
    'https://www.usatoday.com/100-things-do-while-trapped-inside',
    'DrAlone',
    (SELECT MAX(vote_id) from votes)
);

INSERT INTO votes(upvotes, downvotes) VALUES(37, 14);
INSERT INTO posts(community_id, title, description, username, vote_id)
VALUES(
    (SELECT community_id FROM community WHERE community_name='coronavirus'),
    'Remember to do this!',
    'Maintain a 6ft distance between you and others.',
    'healthLvr',
    (SELECT MAX(vote_id) from votes)
);

COMMIT;
