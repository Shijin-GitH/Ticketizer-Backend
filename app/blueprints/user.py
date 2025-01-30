from flask import Blueprint, request, jsonify
from app.config import get_db_connection
import bcrypt

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
        conn = get_db_connection()
        cur = conn.cursor()

        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cur.execute("""
            INSERT INTO Users (Name, Email, Phone, Address, Password_Hash, Profile_Pic)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, email, phone, address, password_hash.decode('utf-8'), profile_pic))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'message': 'User created successfully!'}), 201
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
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT Password_Hash FROM Users WHERE Email = %s", (email,))
        result = cur.fetchone()

        if result is None:
            return jsonify({'error': 'Invalid email or password'}), 401

        stored_password_hash = result[0]

        # Verify the password
        if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            return jsonify({'message': 'Login successful!'}), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()