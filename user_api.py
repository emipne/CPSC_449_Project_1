import flask
from flask import request, jsonify, g, current_app
import sqlite3

######################
# API USAGE
# Caddy Web server route for this API: localhost:$PORT/users/
# Caddy Web server PORT is set to 2015
# --------------------
# Create a new post: Send a POST request to route of register() fn
# Example request:
#   curl -i -X POST -H 'Content-Type:application/json' -d
#   '{"username":"axel", "email":"axel@animalcrossing.com"}'
#   http://localhost:2015/users/register;
# -------------------
# Update user's email: Send a PUT request to route of update_email() fn
# Example request:
#   curl -i -X PUT -H 'Content-Type:application/json' -d '{"username":"axel", "email":"newAxel@animalcrossing.com"}'
#   http://localhost:2015/users/update_email;
# --------------------
# Add one karma from user account: Send a PUT request to route of add_karma() fn
# Example request:
#   curl -i -X PUT -H 'Content-Type:application/json' -d '{"username":"axel"}'
#   http://localhost:2015/users/add_karma;
# --------------------
# Remove one karma from user account: Send a PUT request to route of remove_karma() fn
# Example request:
#   curl -i -X PUT -H 'Content-Type:application/json' -d '{"username":"axel"}'
#   http://localhost:2015/users/remove_karma
# --------------------
# Delete a user: Send a DELETE request to route of delete() fn
# Example request:
#   curl -i -X DELETE http://localhost:2015/users/delete?username=axel;


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
    return jsonify(get_response(status_code=200, message="Welcome to CSUF users API."))


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
# 1. Create user
# 2. Update Email
# 3. Increment Karma
# 4. Decrement Karma
# 5. Deactivate Karma
# function to add a new post to db

# Function to create a new user

@app.route('/register', methods=['POST'])
def register():
    params = request.get_json()
    username = params.get('username')
    email = params.get('email')
    # karma = 1 # all new users should have 1 karma by default

    if not username or not email:
        return jsonify(get_response(status_code=409, message="Username / Email is not provided")), 409

    query = 'SELECT username, email FROM users WHERE username = ? OR email = ?'
    args = (username, email)

    q = query_db(query, args)

    if q:
        return jsonify(get_response(status_code=404, message="Username / Email has been taken")), 404

    query = 'INSERT INTO users (username, email) VALUES (?, ?)'
    args = (username, email)
    q = query_db(query, args, commit=True)

    if not q:
        return page_not_found(404)

    return jsonify(get_response(status_code=201, message="User created")), 201

@app.route('/update_email', methods=["PUT"])
def updateEmail():
    params = request.get_json()
    username = params.get('username')
    email = params.get('email')

    if not username or not email:
        return jsonify(get_response(status_code=409, message="Username / Email is not provided")), 409

    query = 'SELECT username FROM users WHERE username = ?'
    args = (username,)

    q = query_db(query, args)

    if not q:
        return jsonify(get_response(status_code=404, message="Username not found")), 404

    query = 'UPDATE users SET email = ? WHERE username = ?'
    args = (email, username)

    q = query_db(query, args, commit=True)
    if not q:
        return page_not_found(404)

    return jsonify(get_response(status_code=200, message="Email updated")), 200

@app.route('/add_karma', methods=['PUT'])
def add_karma():
    params = request.get_json()
    username = params.get('username')

    if not username:
        return jsonify(get_response(status_code=409, message="Username is not provided")), 409

    query = 'SELECT username FROM users WHERE username = ?'
    args = (username,)

    q = query_db(query, args)

    if not q:
        return jsonify(get_response(status_code=404, message="Username not found")), 404

    query = 'UPDATE users SET karma = karma + 1 WHERE username = ?'
    args = (username,)
    q = query_db(query, args, commit=True)

    if not q:
        return page_not_found(404)

    return jsonify(get_response(status_code=200, message="Karma added")), 200

@app.route('/remove_karma', methods=['PUT'])
def remove_karma():
    params = request.get_json()
    username = params.get('username')

    if not username:
        return jsonify(get_response(status_code=409, message="Username is not provided")), 409

    query = 'SELECT username FROM users WHERE username = ?'
    args = (username,)

    q = query_db(query, args)

    if not q:
        return jsonify(get_response(status_code=404, message="Username not found")), 404

    query = 'UPDATE users SET karma = karma - 1 WHERE username = ?'
    args = (username,)
    q = query_db(query, args, commit=True)

    if not q:
        return page_not_found(404)

    return jsonify(get_response(status_code=200, message="Karma deducted")), 200

@app.route('/delete', methods=['DELETE'])
def delete():
    params = request.args
    username = params.get('username')

    if not username:
        return jsonify(get_response(status_code=409, message="Username is not provided")), 409

    query = 'SELECT username FROM users WHERE username = ?'
    args = (username,)
    q = query_db(query, args)

    if not q:
        return jsonify(get_response(status_code=404, message="Username not found")), 404

    query = 'DELETE FROM users WHERE username = ?'
    args = (username,)

    q = query_db(query, args, commit=True)
    if not q:
        return page_not_found(404)

    return jsonify(get_response(status_code=200, message="User deleted")), 200

def main():
    app.run()


if __name__ == '__main__':
    main()
