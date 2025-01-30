from flask import Blueprint, request, jsonify
from app.config import get_db_connection

bp = Blueprint('main', __name__)

@bp.route('/create_database', methods=['POST'])
def create_database():
    data = request.get_json()
    db_name = data.get('db_name')

    if not db_name:
        return jsonify({'error': 'Database name is required'}), 400

    try:
        # Connect to the default database
        conn = get_db_connection()
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
        # Connect to the default database
        conn = get_db_connection()
        cur = conn.cursor()

        # Create the sequence, table, and trigger
        create_sequence_query = "CREATE SEQUENCE IF NOT EXISTS user_id_seq START 1;"
        create_table_query = """
        CREATE TABLE IF NOT EXISTS Users (
            User_id VARCHAR(255) PRIMARY KEY,
            Name VARCHAR(255) NOT NULL,
            Email VARCHAR(255) UNIQUE NOT NULL,
            Phone VARCHAR(20),
            Address TEXT,
            Password_Hash VARCHAR(255) NOT NULL,
            Profile_Pic TEXT
        );
        """
        create_function_query = """
        CREATE OR REPLACE FUNCTION generate_user_id() RETURNS TRIGGER AS $$
        BEGIN
            NEW.User_id := 'TZR' || nextval('user_id_seq');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        create_trigger_query = """
        CREATE TRIGGER user_id_trigger
        BEFORE INSERT ON Users
        FOR EACH ROW
        EXECUTE FUNCTION generate_user_id();
        """

        # Execute the queries
        cur.execute(create_sequence_query)
        cur.execute(create_table_query)
        cur.execute(create_function_query)
        cur.execute(create_trigger_query)

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'message': 'User table created successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500