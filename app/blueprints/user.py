# filepath: /D:/Tickertizer/Web/Backend/app/blueprints/user.py
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import User
import bcrypt
import jwt
import datetime

bp = Blueprint('user', __name__)

@bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')
    password = data.get('password')
    profile_pic = data.get('profile_pic')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required'}), 400

    try:
        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create a new user instance
        user = User(name=name, email=email, phone=phone, address=address, password_hash=password_hash, profile_pic=profile_pic)

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