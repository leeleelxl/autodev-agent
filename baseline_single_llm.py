```python
import sqlite3
import hashlib
import jwt
import datetime
import re
import os
from functools import wraps
from flask import Flask, request, jsonify, g

DATABASE = 'auth.db'
SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-change-in-production'

app = Flask(__name__)

# ---------- 数据库初始化 ----------
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
        ''')

# ---------- 辅助函数 ----------
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
    return hashlib.sha256(password.encode()).hexdigest()

def validate_username(username: str):
    if not username or len(username) < 3 or len(username) > 20:
        raise ValueError("Username must be 3-20 characters.")
    if not re.match(r'^\w+$', username):
        raise ValueError("Username must contain only letters, digits, or underscore.")

def validate_password(password: str):
    if not password or len(password) < 6:
        raise ValueError("Password must be at least 6 characters.")

# ---------- 注册 ----------
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json(force=True)
        username = data.get('username')
        password = data.get('password')

        validate_username(username)
        validate_password(password)

        db = get_db()
        cur = db.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cur.fetchone():
            return jsonify({"error": "Username already exists"}), 409

        password_hash = hash_password(password)
        db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                   (username, password_hash))
        db.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "Registration failed"}), 500

# ---------- 登录 ----------
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json(force=True)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        db = get_db()
        user = db.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,)).fetchone()
        if not user or user['password_hash'] != hash_password(password):
            return jsonify({"error": "Invalid credentials"}), 401

        payload = {
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({"token": token}), 200
    except Exception as e:
        return jsonify({"error": "Login failed"}), 500

# ---------- Token 验证装饰器 ----------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            g.user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

# ---------- 受保护示例路由 ----------
@app.route('/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({"message": "Access granted", "user_id": g.user_id}), 200

# ---------- 启动 ----------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
```