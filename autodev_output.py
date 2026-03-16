from flask import Flask, request, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from token_service import TokenService
from database_adapter import DatabaseAdapter

app = Flask(__name__)

# Error Handling
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'message': 'Bad request'}), 400

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        abort(400)
    user = User(data['username'], data['password'])
    user.create()
    return jsonify({'message': 'User registered successfully'}), 201

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        abort(400)
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        token = TokenService.generate_token(user.id)
        return jsonify({'token': token}), 200
    abort(401)

# Token Validation Middleware
@app.before_request
def validate_token():
    if request.endpoint in ['login', 'register']:
        return
    if not TokenService.verify_token(request.headers.get('Authorization')):
        abort(403)

if __name__ == '__main__':
    app.run(debug=True)