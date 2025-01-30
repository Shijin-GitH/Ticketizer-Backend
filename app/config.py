import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables from .env file
load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgres://avnadmin:AVNS_PMmdhDlfRwyLY13PPN-@ticketizer-shijinabraham2003-68db.d.aivencloud.com:18037/defaultdb?sslmode=require")

def get_db_connection(db_name="ticketizer"):
    # Parse the DATABASE_URL and replace the database name
    conn_str = Config.DATABASE_URL
    if db_name:
        conn_str = conn_str.rsplit('/', 1)[0] + '/' + db_name + '?sslmode=require'
    conn = psycopg2.connect(conn_str)
    return conn