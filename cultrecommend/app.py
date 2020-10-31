from flask import (
    Flask,
    jsonify,
    render_template
)
import os
import sqlite3
import sys

app = Flask(__name__, static_url_path='/static')
db_path = os.environ.get('DB_PATH', default=None)
if not db_path:
    sys.stderr.write('FATAL ERROR: no DB_PATH provided.\n')
    exit(1)
try:
    connection = sqlite3.connect(db_path)
except:
    sys.stderr.write("FATAL ERROR: bad connection to database. Exception's output below.\n\n")
    raise
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
        return {'error': 'No uid specified.'}, 400

    try:
        connection = sqlite3.connect(db_path)
        cursor.execute("SELECT * FROM users WHERE id = '{}';".format(uid))
        connection.commit()
        uinfo = cursor.fetchone()
        if uinfo:
            scheme = [description[0] for description in cursor.description]
            result = {kv[0]: kv[1] for kv in zip(scheme, uinfo)}, 200
    except sqlite3.Error as error:
        result = {'error', 'Database error, message: "{}"'.format(error.args[0])}, 500
    finally:
        if connection:
            connection.close()
    
    if result is not None:
        return err_result
    else:
        return {'error': 'No result.'}, 500
