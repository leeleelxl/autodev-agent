```python
import sqlite3
import os
import jwt
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configurations
SECRET_KEY = os.urandom(32)  # You should store this securely
ALGORITHM = "HS256"
DATABASE = "sqlite:///./auth.db"

# Create the database if it does not exist
conn = sqlite3.connect(DATABASE)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
)
''')
conn.commit()
conn.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Missing data'}), 400

    try:
        password_hash = generate_password_hash(password)
    except Exception as e:
        return jsonify({'error': 'Error hashing password'}), 500

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    except Exception as e:
        return jsonify({'error': 'Error registering user'}), 500
    finally:
        conn.close()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Missing data'}), 400

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()

    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    try:
        if not check_password_hash(user[0], password):
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': 'Error checking password'}), 500

    try:
        payload = {'username': username}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        return jsonify({'error': 'Error generating token'}), 500

    return jsonify({'token': token})

@app.route('/verify', methods=['POST'])
def verify():
    token = request.json.get('token')
    if not token:
        return jsonify({'error': 'Token is missing'}), 400

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('username')
        if not username:
            return jsonify({'error': 'Invalid token'}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Token is valid'}), 200

if __name__ == '__main__':
    app.run(debug=True)
```