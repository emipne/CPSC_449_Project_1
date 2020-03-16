import flask
from flask import request, jsonify, g, current_app
import sqlite3

######################
# API USAGE
# Caddy Web server route for this API: localhost:$PORT/posts/
# Caddy Web server PORT is set to 2015
# --------------------
# Create a new post: Send a POST request to route of create_post() fn
# Example request:
#   curl -i -X POST -H 'Content-Type:application/json' -d
#   '{"title":"Test post", "description":"This is a test post", "username":"some_guy_or_gal", "community_name":"449"}'
#   http://localhost:2015/posts/create;
# --------------------
# Delete an existing post: Send a GET request to route of delete_post() fn
# Example request:
# curl -i -X DELETE http://localhost:2015/posts/delete?post_id=4;
# --------------------
# Retrieve an existing post: Send a GET request to route of get_post() fn
# Example request:
#   curl -i http://localhost:2015/posts/get?post_id=2;
# --------------------
# List the n most recent posts to a particular community:
#   Send a GET request to route of get_posts_filter() fn with args (community_name and n)
# Example request:
# curl -i http://localhost:2015/posts/filter?n=2&community_name=algebra;
# --------------------
# List the n most recent posts to any community:
#   Send a GET request to route of get_posts_filter() fn with args (n)
# Example request:
# curl -i http://localhost:2015/posts/filter?n=2

# config variables
DATABASE = 'data.db'
DEBUG = True

######################
app = flask.Flask(__name__)
app.config.from_object(__name__)

######################
# Database
# app.config.from_envvar('APP_CONFIG')
# db_name: data.db

# table1: posts
# post_id
# community_id
# title
# description
# resource_url
# published
# username
# vote_id

# table2: votes
# vote_id
# upvotes
# downvotes

# table3: community
# community_id
# name


######################
# helper function used to convert each query result row into dictionary
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


# helper function to generate a response with status code and message
def get_response(status_code, message):
    return {"status_code": str(status_code), "message": str(message)}


# get db from flask g namespace
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = make_dicts
    return g.db


# initiate db with
# $FLASK_APP=post_api.py
# $flask init
@app.cli.command('init')
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('data.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# close db connection
@app.teardown_appcontext
def close_db(e=None):
    if e is not None:
        print(f'Closing db: {e}')
    db = g.pop('db', None)
    if db is not None:
        db.close()


# home page
@app.route('/', methods=['GET'])
def home():
    return jsonify(get_response(status_code=200, message="Welcome to CSUF Discussions Post API."))


# 404 page
@app.errorhandler(404)
def page_not_found(status_code=404):
    error_json = get_response(status_code=status_code, message="Resource not found")
    return jsonify(error_json), status_code


# function to execute a single query at once
def query_db(query, args=(), one=False, commit=False):
    # one=True means return single record
    # commit = True for post and delete query (return boolean)
    conn = get_db()
    try:
        rv = conn.execute(query, args).fetchall()
        if commit:
            conn.commit()
    except sqlite3.OperationalError as e:
        print(e)
        return False
    close_db()
    if not commit:
        return (rv[0] if rv else None) if one else rv
    return True


# function to execute multiple queries at once (also fn commits the transaction)
def transaction_db(query, args, return_=False):
    # return_=True if the transaction needs returns a result
    conn = get_db()
    if len(query) != len(args):
        raise ValueError('arguments dont match queries')
    try:
        rv = []
        conn.execute('BEGIN')
        for i in range(len(query)):
            rv.append(conn.execute(query[i], args[i]).fetchall())
        conn.commit()
    except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
        conn.execute('rollback')
        print('Transaction failed. Rolled back')
        print(e)
        return False
    close_db()
    return True if not return_ else rv


# function to retrieve a single post with post_id
@app.route('/get', methods=['GET'])
def get_post():
    params = request.args
    post_id = params.get('post_id')
    if not post_id:
        return page_not_found(404)
    query = 'SELECT post_id, title, description, resource_url, published, username, community_name FROM posts ' \
            'INNER JOIN community ON posts.community_id=community.community_id WHERE post_id=?'
    args = (post_id,)
    q = query_db(query, args, one=True)
    if q:
        return jsonify(q), 200
    return page_not_found(404)


# function to retrieve posts with filters for a number of posts n (default value of n is 100)
@app.route('/filter', methods=['GET'])
def get_posts_filter():
    params = request.args
    query = 'SELECT post_id, title, published, username, community_name FROM posts ' \
             'INNER JOIN community ON posts.community_id=community.community_id WHERE'
    args = []

    post_id = params.get('post_id')
    filters = 0
    if post_id:
        query += ' post_id=? AND'
        args.append(post_id)
        filters += 1

    username = params.get('username')
    if username:
        query += ' username=? AND'
        args.append(username)
        filters += 1

    published = params.get('published')
    if published:
        query += ' published=? AND'
        args.append(published)
        filters += 1

    title = params.get('title')
    if title:
        query += ' title=? AND'
        args.append(title)
        filters += 1

    community_name = params.get('community_name')
    if community_name:
        query += ' community_name=? AND'
        args.append(community_name)
        filters += 1

    if filters > 0:
        query = query[:-4]
    else:
        query = query[:-6]

    number = params.get('n')
    if not number:
        number = 100
    count_query = 'SELECT COUNT(post_id) FROM '
    query += ' ORDER BY published DESC LIMIT ?;'
    args.append(number)

    q = query_db(query, tuple(args))
    if q:
        return jsonify(q), 200
    return page_not_found(404)


# function to add a new post to db
@app.route('/create', methods=['POST'])
def create_post():
    params = request.get_json()
    community_name = params.get('community_name')
    title = params.get('title')
    username = params.get('username')
    description = params.get('description')
    resource_url = params.get('resource_url')

    if not title or not username or not community_name:
        return jsonify(get_response(status_code=409, message="username / title / community_name is not in request"))
    query1 = 'INSERT INTO votes (upvotes, downvotes) VALUES (?, ?)'
    args1 = (0, 0)
    

    query_community = 'SELECT community_id FROM community WHERE community_name=?'
    args_community = (community_name,)
    community_id = query_db(query_community, args_community, one=True, commit=False)
    query4 = 'SELECT last_insert_rowid();'
    args4 = ()
    if community_id is not None:
        if type(community_id) == list:
            id_ = community_id[0]['community_id']
        else:
            id_ = community_id['community_id']

        query3 = 'INSERT INTO posts (community_id, title, description, resource_url, username, vote_id) ' \
                 'VALUES (?,?,?,?,?,(SELECT MAX(vote_id) FROM votes))'
        args3 = (id_, title, description, resource_url, username)
        q = transaction_db(query=[query1, query3, query4], args=[args1, args3, args4], return_=True)
    else:
        query2 = 'INSERT INTO community (community_name) VALUES (?)'
        args2 = (community_name,)
        query3 = 'INSERT INTO posts (community_id, title, description, resource_url, username, vote_id) ' \
                 'VALUES ((SELECT community_id FROM community WHERE community_name=?),?,?,?,?,(SELECT MAX(vote_id) FROM votes))'
        args3 = (community_name, title, description, resource_url, username)
        q = transaction_db(query=[query1, query2, query3, query4], args=[args1, args2, args3, args4], return_=True)
    if not q:
        return page_not_found(404)
    rowid = q[-1][0]["last_insert_rowid()"]
    response = jsonify(get_response(status_code=201, message="Post created"))
    response.status_code = 201
    response.headers['location'] = "http://localhost:2015/posts/get?post_id=" + str(rowid)
    response.autocorrect_location_header = False
    return response


# function to delete an existing post from db
@app.route('/delete', methods=['DELETE'])
def delete_post():
    params = request.args

    post_id = params.get('post_id')
    if not post_id:
        return page_not_found(404)

    query1 = 'SELECT * FROM posts WHERE post_id=?'
    args1 = (post_id,)
    if not query_db(query1, args1):
        return jsonify(get_response(status_code=404, message="Post does not exist")), 404

    query2 = 'DELETE FROM votes WHERE vote_id=(SELECT vote_id FROM posts WHERE post_id=?)'
    args2 = (post_id,)

    query3 = 'DELETE FROM posts WHERE post_id=?'
    args3 = (post_id,)

    q = transaction_db([query2, query3], [args2, args3])
    if not q:
        return page_not_found(404)
    return jsonify(get_response(status_code=200, message="Post deleted")), 200


def main():
    app.run()


if __name__ == '__main__':
    main()
