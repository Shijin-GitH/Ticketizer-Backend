import os

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgres://avnadmin:AVNS_PMmdhDlfRwyLY13PPN-@ticketizer-shijinabraham2003-68db.d.aivencloud.com:18037/defaultdb?sslmode=require")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

def get_db_connection():
    import psycopg2
    conn = psycopg2.connect(Config.DATABASE_URL)
    return conn