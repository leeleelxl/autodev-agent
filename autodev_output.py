# app.py
from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_pyjwt import PyJWT
from models import User, UserSchema
from token_service import generate_token, verify_token

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# User Registration
@app.route('/register', methods=['POST'])
def register():
    user_schema = UserSchema()
    load = user_schema.load
    try:
        data = load(request.get_json())
    except Exception as e:
        return make_response(jsonify({'errors': str(e)}), 422)
    if User.query.filter_by(email=data['email']).first():
        return make_response(jsonify({'message': 'Email already exists'})), 409
    hashed_password = generate_password_hash(data['password'], method='sha256')
    user = User(email=data['email'], password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return make_response(jsonify({'message': 'User created successfully.'})), 201

# User Login
@app.route('/login', methods=['POST'])
def login():
    user_schema = UserSchema()
    load = user_schema.load
    try:
        data = load(request.get_json())
    except Exception as e:
        return make_response(jsonify({'errors': str(e)}), 422)
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return make_response(jsonify({'message': 'Invalid credentials'})), 401
    access_token = generate_token(user.id)
    return jsonify(access_token=access_token), 200

# Error Handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'})), 404

if __name__ == '__main__':
    app.run(debug=True)
