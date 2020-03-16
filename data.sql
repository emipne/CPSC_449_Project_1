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

INSERT INTO votes(upvotes, downvotes) VALUES(100, 25);
INSERT INTO community(community_id, community_name) VALUES(1, 'algebra');
INSERT INTO posts(community_id, title, description, resource_url, username, vote_id)
VALUES(
    (SELECT community_id FROM community WHERE community_name='algebra'),
    'Algebra post 1',
    'Some quadratic formula',
    'http://fullerton.edu',
    'math_guy_1',
    (SELECT MAX(vote_id) from votes)
);

INSERT INTO votes(upvotes, downvotes) VALUES(99, 24);
INSERT INTO community(community_id, community_name) VALUES(2, 'calculus');
INSERT INTO posts(community_id, title, description, username, vote_id)
VALUES(
    (SELECT community_id FROM community WHERE community_name='calculus'),
    'Calculus post 1',
    'Steps to integrate',
    'math_guy_1',
    (SELECT MAX(vote_id) from votes)
);

INSERT INTO votes(upvotes, downvotes) VALUES(98, 23);
INSERT INTO posts(community_id, title, description, resource_url, username, vote_id)
VALUES(
    (SELECT community_id FROM community WHERE community_name='calculus'),
    'Calculus post 2',
    'Steps to differentiate',
    'https://www.google.com',
    'math_guy_2',
    (SELECT MAX(vote_id) from votes)
);

INSERT INTO votes(upvotes, downvotes) VALUES(97, 22);
INSERT INTO posts(community_id, title, description, username, vote_id)
VALUES(
    (SELECT community_id FROM community WHERE community_name='calculus'),
    'Calculus post 3',
    'Differentiation is rate of change',
    'math_guy_2',
    (SELECT MAX(vote_id) from votes)
);

COMMIT;
