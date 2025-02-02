# filepath: /D:/Tickertizer/Web/Backend/app/blueprints/user.py
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import User
import bcrypt
import jwt
import datetime
from flask_mail import Message, Mail
import random
import string
from functools import wraps

bp = Blueprint('user', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(User_id=data['user_id']).first()
        except:
            return jsonify({'error': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    profile_pic = data.get('profile_pic')
    role = data.get('role')

    if not name or not email or not password or not phone:
        return jsonify({'error': 'Name, email, phone, and password are required'}), 400
    elif User.query.filter_by(Email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    try:
        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create a new user instance
        user = User(name=name, email=email, phone=phone, password_hash=password_hash, profile_pic=profile_pic, role=role)

        # Add the user to the session and commit
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'User created successfully!', 'user_id': user.formatted_user_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    try:
        # Query the user by email
        user = User.query.filter_by(Email=email).first()

        if user is None:
            return jsonify({'error': 'Invalid email or password'}), 401

        # Verify the password
        if bcrypt.checkpw(password.encode('utf-8'), user.Password_Hash.encode('utf-8')):
            # Generate JWT token
            token = jwt.encode({
                'user_id': user.User_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
            }, current_app.config['SECRET_KEY'], algorithm='HS256')

            return jsonify({'message': 'Login successful!', 'token': token}), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    try:
        # Query the user by id
        user = User.query.get(user_id)

        if user is None:
            return jsonify({'error': 'User not found'}), 404

        # Delete the user
        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': 'User deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# @bp.route('/forget-password', methods=['POST'])
# def forget_password():
#     data = request.get_json()
#     email = data.get('email')

#     if not email:
#         return jsonify({'error': 'Email is required'}), 400

#     try:
#         # Query the user by email
#         user = User.query.filter_by(email=email).first()

#         if user is None:
#             return jsonify({'error': 'Email not found'}), 404

#         # Generate a random code
#         code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

#         # Send the code to the user's email
#         msg = Message('Password Reset Code', sender='noreply@tickertizer.com', recipients=[email])
#         msg.body = f'Your password reset code is {code}'
#         Mail.send(msg)

#         return jsonify({'message': 'Password reset code sent to your email'}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
