from flask import (
    Flask,
    jsonify,
    render_template,
    request,
)
import os
import sqlite3
import sys

global columns
app = Flask(__name__, static_url_path='/static')
db_path = os.environ.get('DB_PATH', default=None)
if not db_path:
    sys.stderr.write('FATAL ERROR: no DB_PATH provided.\n')
    exit(1)
try:
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info('users');")
    connection.commit()
    res = cursor.fetchall()
    columns = frozenset(column[1] for column in res)
except:
    sys.stderr.write("FATAL ERROR: bad connection to database. Exception's output below.\n\n")
    raise
finally:
    if connection:
        connection.close()


@app.route('/')
def index():
    return render_template('landing.html')


@app.route('/api/v1/get_user_info', methods=['GET'])
def get_user_info():
    uid = request.args.get('uid')
    result = None

    if not uid or len(uid) == 0:
        return jsonify({'error': 'No uid specified.'}), 400

    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = '{}';".format(uid))
        connection.commit()
        uinfo = cursor.fetchone()
        if uinfo:
            scheme = [description[0] for description in cursor.description]
            result = jsonify({kv[0]: kv[1] for kv in zip(scheme, uinfo)}), 200
        else:
            result = jsonify({'error': 'No user id found.'}), 400
    except sqlite3.Error as error:
        result = jsonify({'error', 'Database error, message: "{}"'.format(error.args[0])}), 500
    finally:
        if connection:
            connection.close()
    
    if result is not None:
        return result
    else:
        return jsonify({'error': 'Unknown error.'}), 500


@app.route('/api/v1/modify_users', methods=['POST'])
def modify_users():
    try:
        data = request.get_json()
    except:
        return jsonify({'error': 'Malformed JSON.'}), 400

    ids = []
    if type(data) == type(dict()):
        if not 'id' in data:
            return jsonify({'error': "Missing field 'id' in data."}), 400
        ids = [str(data['id'])]
    elif type(data) == type(list()):
        for user in data:
            if not 'id' in user:
                return jsonify({'error': "Missing field 'id' in data."}), 400
            ids.append(str(user['id']))
    else:
        return jsonify({'error': "Unsupported object. Only dictionary and list are allowed."}), 400

    not_inserted = []
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        if type(data) == type(dict()):
            data = [data]

        for user in data:
            try:
                cursor.executescript(__build_request(user))
                connection.commit()
            except sqlite3.Error as error:
                user['error_msg'] = str(error)
                not_inserted.append(user)
    except sqlite3.Error:
        pass
    finally:
        if connection:
            connection.close()
    
    if len(not_inserted) > 0:
        return jsonify({
            'Error': "Some users could not be inserted or updated. Check 'error_msg' field in users.", 
            'Users': not_inserted
            }), 500
    else:
        return jsonify({'Message': 'All OK.'}), 200


def __sqlite_escape_string(string):
    return string.replace("'", "''")


def __build_request(data):
    request = 'INSERT OR IGNORE INTO users ({0}) VALUES({1});\nUPDATE users SET {2} WHERE id={3};'
    keys, values = list(), list()

    for key in data:
        keys.append(__sqlite_escape_string(str(key)))
        values.append("'" + __sqlite_escape_string(str(data[key])) + "'")

    return request.format(
        ', '.join(keys), 
        ', '.join(values), 
        ', '.join("'" + __sqlite_escape_string(str(key)) + "' = '" + __sqlite_escape_string(str(data[key])) + "'" for key in data), 
        str(data['id'])
    )
