import sqlite3
import hashlib
import jwt
import datetime
import re
import os
from functools import wraps
from flask import Flask, request, jsonify, g

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-key-change-in-production')

DB_NAME = 'users.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_NAME)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def validate_username(username):
    if not isinstance(username, str) or not username:
        return False
    if len(username) < 3 or len(username) > 20:
        return False
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False
    return True

def validate_password(password):
    if not isinstance(password, str) or not password:
        return False
    if len(password) < 6:
        return False
    return True

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['username']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password are required'}), 400
    username = data['username']
    password = data['password']
    if not validate_username(username):
        return jsonify({'message': 'Invalid username format'}), 400
    if not validate_password(password):
        return jsonify({'message': 'Password must be at least 6 characters'}), 400
    db = get_db()
    try:
        db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                   (username, hash_password(password)))
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Username already exists'}), 409
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password are required'}), 400
    username = data['username']
    password = data['password']
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    if not user or user['password_hash'] != hash_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401
    token = jwt.encode({
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token})

@app.route('/verify', methods=['GET'])
@token_required
def verify(current_user):
    return jsonify({'message': 'Token is valid', 'username': current_user})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
