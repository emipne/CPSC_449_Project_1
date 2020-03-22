-- $ sqlite3 data.db < data.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS votes;
DROP TABLE IF EXISTS community;
DROP TABLE IF EXISTS posts;

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
    community_id VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    description VARCHAR,
    resource_url VARCHAR,
    published TIMESTAMP DEFAULT (DATETIME('now', 'localtime')),
    username VARCHAR NOT NULL,
    vote_id INTEGER NOT NULL,
    FOREIGN KEY (vote_id) REFERENCES votes (vote_id),
    FOREIGN KEY (community_id) REFERENCES community (community_id)
);

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
