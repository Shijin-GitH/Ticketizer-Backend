from flask import Blueprint, request, jsonify
from app import db
from app.models import User
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

bp = Blueprint('main', __name__)

@bp.route('/create_database', methods=['POST'])
def create_database():  
    data = request.get_json()
    db_name = data.get('db_name')

    if not db_name:
        return jsonify({'error': 'Database name is required'}), 400

    try:
        # Connect to the default database
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        conn.autocommit = True
        cur = conn.cursor()

        # Create the new database
        cur.execute(f"CREATE DATABASE {db_name}")

        cur.close()
        conn.close()

        return jsonify({'message': f'Database {db_name} created successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/create_user_table', methods=['POST'])
def create_user_table():
    try:
        # Create the Users table using SQLAlchemy ORM
        db.create_all()

        return jsonify({'message': 'User table created successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500