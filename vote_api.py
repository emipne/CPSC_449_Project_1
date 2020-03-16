import flask
from flask import request, jsonify, g, current_app
import sqlite3

######################
# API USAGE
# Caddy Web server route for this API: localhost:$PORT/votes/
# Caddy Web server PORT is set to 2015
# --------------------
# Upvote a post:
# Example request:
#   curl -i 'http://localhost:2015/votes/upvotes?vote_id=2';
#
# --------------------
# Downvote a post:
# Example request:
# 	curl -i 'http://localhost:2015/votes/downvotes?vote_id=1';
# --------------------
# Report the number of upvotes and downvotes for a post:
# Example request:
#   curl -i 'http://localhost:2015/votes/get?vote_id=2';
# --------------------
# List the n top-scoring posts to any community:
# Example request:
# 	curl -i 'http://localhost:2015/votes/getTop?n=3';
# --------------------
# Given a list of post identifiers, return the list sorted by score.:
# Example request:
#	curl 'http://localhost:2015/votes/getList?post_ids=1,2,3';

######################
# References Used:
# https://stackoverflow.com/questions/2602043/rest-api-best-practice-how-to-accept-list-of-parameter-values-as-input

######################

# config
DATABASE = 'data.db'
DEBUG = True

app = flask.Flask(__name__)
app.config.from_object(__name__)


######################
# app.config.from_envvar('APP_CONFIG')
# db_name: data.db

# table1: posts
#	post_id
#	community_id
#	title
# 	description
#	published
#	username
#	vote_id

# table2: votes
# 	vote_id
# 	upvotes
#	downvotes

# table3: community
#	community_id
#	name
######################

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


# helper function to generate a response with status code and message
def get_response(status_code, message):
    return {"status_code": str(status_code), "message": str(message)}


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = make_dicts
    return g.db


def query_db(query, args=(), one=False, commit=True):
    # one=True means return single record
    # commit = True for post and delete query
    conn = get_db()
    try:
        rv = conn.execute(query, args).fetchall()
        if commit:
            conn.commit()
    except sqlite3.OperationalError as e:
        print(e)
        return page_not_found(404)
    close_db()
    if not commit:
        return (rv[0] if rv else None) if one else rv
    return True


def transaction_db(query, args):
    conn = get_db()
    if len(query) != len(args):
        raise ValueError('arguments dont match queries')
    try:
        conn.execute('BEGIN')
        for i in range(len(query)):
            conn.execute(query[i], args[i])
        conn.commit()
    except sqlite3.OperationalError as e:
        conn.execute('rollback')
        print(e)

    close_db()
    return 'Transaction Completed'


@app.cli.command('init')
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('data.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# home page
@app.route('/', methods=['GET'])
def home():
    return "<h1>Welcome to CSUF Discussions API</h1>" \
           "<p>Use /votes for votes api</p>"


@app.errorhandler(404)
def page_not_found(status_code=404):
    error_json = get_response(status_code=status_code, message="Resource not found")
    return jsonify(error_json), status_code


# function to retrieve all votes without any filters
# curl 'http://127.0.0.1:5000/all;
@app.route('/all', methods=['GET'])
def get_posts_all():
    query = 'SELECT * FROM votes'
    all_votes = query_db(query, commit=False)
    return jsonify(all_votes), 200


# Upvote a post
# curl -i -X POST -H "Content-Type: application/json" -d '{"vote_id":"2"}' 'http://127.0.0.1:5000/upvotes'
@app.route('/upvotes', methods=['POST'])
def get_upvotes():
    params = request.get_json()
    # params = request.args
    vote_id = params.get('vote_id')
    if not vote_id:
        return page_not_found(404)
    query = 'UPDATE votes SET upvotes=upvotes + 1 WHERE vote_id IN (SELECT vote_id FROM posts WHERE post_id = ?)'
    args = (vote_id,)
    update_upvotes = query_db(query, args, one=True)
    if update_upvotes:
        # return jsonify(get_response(status_code=201, message=))
        return jsonify(update_upvotes), 201
    return page_not_found(404)


# Downvote a post
# curl -i -X POST -H "Content-Type: application/json" -d '{"vote_id":"2"}' 'http://127.0.0.1:5000/downvotes'
@app.route('/downvotes', methods=['POST'])
def get_downvotes():
    params = request.get_json()

    # params = request.args
    vote_id = params.get('vote_id')
    if not vote_id:
        return page_not_found(404)
    query = 'UPDATE votes SET downvotes=downvotes+1 WHERE vote_id IN (SELECT vote_id FROM posts WHERE post_id = ?)'
    args = (vote_id,)
    update_downvotes = query_db(query, args, one=True)
    if update_downvotes:
        return jsonify(update_downvotes), 201
    return page_not_found(404)


# Report the number of upvotes and downvotes for a post
# curl -i 'http://127.0.0.1:5000/get?vote_id=2';
@app.route('/get', methods=['GET'])
def get_retrievevotes():
    params = request.args
    vote_id = params.get('vote_id')
    if not vote_id:
        return page_not_found(404)
    query = 'SELECT upvotes,downvotes FROM votes INNER JOIN posts ON posts.vote_id = votes.vote_id WHERE post_id = ?'
    args = (vote_id,)
    update_get = query_db(query, args, commit=False)
    if update_get:
        return jsonify(update_get), 200
    return page_not_found(404)


# List the n top-scoring posts to any community
# curl 'http://127.0.0.1:5000/getTop?n=3';
@app.route('/getTop', methods=['GET'])
def get_topvotes():
    params = request.args
    n = params.get('n')
    if not n:
        return page_not_found(404)
    query = 'SELECT posts.post_id FROM posts INNER JOIN votes on posts.vote_id = votes.vote_id ORDER BY abs(upvotes-downvotes) DESC LIMIT ?'
    args = (n,)
    update_getTop = query_db(query, args, commit=False)
    if update_getTop:
        return jsonify(update_getTop), 200
    return page_not_found(404)


# Given a list of post identifiers, return the list sorted by score.
# curl -i -X POST -H "Content-Type: application/json" -d '{"post_ids":["1","2","3"]}' 'http://127.0.0.1:5000/getList'
@app.route('/getList', methods=['POST'])
def get_topList():
    params = request.get_json()

    post_ids = params.get('post_ids')

    if not post_ids:
        return page_not_found(404)

    post_ids = list(map(int, post_ids))
    t = tuple(post_ids)
    query = 'SELECT votes.vote_id,upvotes,downvotes FROM posts inner join votes on posts.vote_id = votes.vote_id WHERE posts.post_id IN {} ORDER BY (upvotes-downvotes) DESC'.format(
        t)
    # print(query)
    args = (post_ids,)
    update_getList = query_db(query, commit=False)
    if update_getList:
        return jsonify(update_getList), 200
    return page_not_found(404)


def main():
    app.run()


if __name__ == '__main__':
    main()
