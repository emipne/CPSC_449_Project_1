import flask
from flask import request, jsonify, g, current_app
import sqlite3

######################
# API USAGE
# Caddy Web server route for this API: localhost:$PORT/messages/
# Caddy Web server PORT is set to 2015
# --------------------
# Send a message: Send a POST request to route of send() fn
# Example request:
#   curl -i -X POST -H 'Content-Type:application/json' -d
#   '{"user_from":"ilovedog", "user_to":"ilovecat", "msg_content":"I think dogs are better", "msg_flag":"greetings"}'
#   http://localhost:2015/messages/send;
# --------------------
# Delete a message: Send a DELETE request to route of delete() fn
# Example request:
# curl -i -X DELETE http://localhost:2015/messages/delete?msg_id=2;
# --------------------
# Favorite a message: Send a POST request to route of favorite() fn
# Example request:
# curl -i -X POST -H 'Content-Type:application/json' http://localhost:2015/messages/favorite?msg_id=1;


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

# table1: users
# user_id
# username
# email
# karma

# table2: messages
# msg_id
# user_from
# user_to
# msg_time
# msg_content
# msg_flag

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
    return jsonify(get_response(status_code=200, message="Welcome to CSUF messages API."))


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

### WHAT TO DO ###
# 1. Send message
# 2. Delete message
# 3. Favorite message

@app.route('/send', methods=['POST'])
def send():
    params = request.get_json()
    user_from = params.get('user_from')
    user_to = params.get('user_to')
    msg_content = params.get('msg_content')
    msg_flag = params.get('msg_flag')

    if not user_from or not user_to:
        return jsonify(get_response(status_code=409, message="Sender / Recipient is not provided")), 409

    query1 = 'SELECT username FROM users WHERE username = ?'
    args1 = (user_from,)
    q_sender = query_db(query1, args1)

    query2 = "SELECT username FROM users WHERE username = ?"
    args2 = (user_to,)
    q_receiver = query_db(query2, args2)

    if not q_sender:
        return jsonify(get_response(status_code=404, message="Sender not existed")), 404
    if not q_receiver:
        return jsonify(get_response(status_code=404, message="Receiver not existed")), 404

    query = 'INSERT INTO messages (user_from, user_to, msg_content, msg_flag) VALUES ((SELECT user_id FROM users WHERE username=?), (SELECT user_id FROM users WHERE username=?), ?, ?)'
    args = (user_from, user_to, msg_content, msg_flag)
    q = transaction_db(query=[query], args=[args], return_=True)

    if not q:
        return page_not_found(404)

    return jsonify(get_response(status_code=201, message="Message sent")), 201

@app.route('/delete', methods=['DELETE'])
def delete():
    params = request.args
    msg_id = params.get('msg_id')
    if not msg_id:
        return jsonify(get_response(status_code=409, message="Message ID is not provided")), 409

    query = 'SELECT msg_id FROM messages WHERE msg_id = ?'
    args = (msg_id,)
    q = query_db(query, args)

    if not q:
        return jsonify(get_response(status_code=404, message="Message not existed")), 404

    query = 'DELETE FROM favorite WHERE msg_id = ?'
    args = (msg_id,)
    query1 = 'DELETE FROM messages WHERE msg_id = ?'

    q = transaction_db([query, query1], [args, args],)

    if not q:
        return page_not_found(404)

    return jsonify(get_response(status_code=200, message="Message deleted")), 200

@app.route('/favorite', methods=['POST'])
def favorite():
    params = request.args
    msg_id = params.get('msg_id')
    if not msg_id:
        return jsonify(get_response(status_code=409, message="Message ID is not provided")), 409
    query = 'SELECT msg_id FROM messages WHERE msg_id = ?'
    args = (msg_id,)
    q = query_db(query, args)

    if not q:
        return jsonify(get_response(status_code=404, message="Message not existed")), 404

    query2 = 'SELECT msg_id FROM favorite WHERE msg_id = ?'
    args2 = (msg_id,)
    q1 = query_db(query2,args2)

    if q1:
        return jsonify(get_response(status_code=404, message="Message already favorited")), 404

    query = 'INSERT INTO favorite (msg_ID) VALUES (?)'
    args = (msg_id,)
    q = query_db(query, args, commit=True)

    if not q:
        return page_not_found(404)

    return jsonify(get_response(status_code=201, message="Message favorited")), 201

def main():
    app.run()

if __name__ == '__main__':
    main()
