```python
import sqlite3
import jwt
import hashlib
import os
from getpass import getpass
from datetime import datetime, timedelta

# Configuration
SECRET_KEY = 'your_secret_key'
ALGORITHM = 'HS256'
EXPIRE_MINUTES = 30  # Token validity period
DB_PATH = 'users.db'

# Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create table for users
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)''')
conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password):
    if not username or not password:
        raise ValueError("Username and password cannot be empty")
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    if c.fetchone() is not None:
        raise ValueError("Username already exists")
    password_hash = hash_password(password)
    c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
    conn.commit()
    return True

def login(username, password):
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    if not user:
        raise ValueError("Username not found")
    if hash_password(password) != user[1]:
        raise ValueError("Incorrect password")
    return create_token(username)

def create_token(username):
    payload = {
        'exp': datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES),
        'iat': datetime.utcnow(),
        'sub': username
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        c.execute("SELECT * FROM users WHERE username = ?", (payload['sub'],))
        if c.fetchone():
            return True
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
    return False

def main():
    while True:
        print("\n1. Register")
        print("2. Login")
        print("3. Verify Token")
        print("4. Exit")
        choice = input("Enter choice: ")
        if choice == '1':
            username = input("Enter username: ")
            password = getpass("Enter password: ")
            try:
                register(username, password)
                print("Registration successful")
            except ValueError as e:
                print(e)
        elif choice == '2':
            username = input("Enter username: ")
            password = getpass("Enter password: ")
            try:
                token = login(username, password)
                print("Login successful. Token:", token)
            except ValueError as e:
                print(e)
        elif choice == '3':
            token = input("Enter token to verify: ")
            if verify_token(token):
                print("Token verified successfully")
            else:
                print("Token verification failed")
        elif choice == '4':
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
```