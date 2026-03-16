```python
import sqlite3
import hashlib
import jwt
import re
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, g

DATABASE = 'auth.db'
SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-key-change-in-production')

app = Flask(__name__)

# ---------- 数据库初始化 ----------
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# ---------- 工具函数 ----------
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def validate_username(username: str):
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        raise ValueError("Username must be 3-20 characters, alphanumeric/underscore only.")

def validate_password(password: str):
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters.")

def generate_token(username: str) -> str:
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

# ---------- 装饰器 ----------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header missing'}), 401
        try:
            token = auth_header.split(" ")[1]
            username = verify_token(token)
            g.current_user = username
        except (IndexError, ValueError) as e:
            return jsonify({'error': str(e)}), 401
        return f(*args, **kwargs)
    return decorated

# ---------- 路由 ----------
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    try:
        validate_username(username)
        validate_password(password)
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400

    db = get_db()
    existing = db.execute('SELECT 1 FROM users WHERE username = ?', (username,)).fetchone()
    if existing:
        return jsonify({'error': 'Username already exists'}), 409

    password_hash = hash_password(password)
    try:
        db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                   (username, password_hash))
        db.commit()
    except sqlite3.Error:
        return jsonify({'error': 'Database error'}), 500

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    db = get_db()
    user = db.execute('SELECT password_hash FROM users WHERE username = ?', (username,)).fetchone()
    if not user or user['password_hash'] != hash_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = generate_token(username)
    return jsonify({'token': token}), 200

@app.route('/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({'message': f'Hello, {g.current_user}! This is a protected route.'}), 200

# ---------- 启动 ----------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
```