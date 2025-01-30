from flask import Flask
from app.routes import bp
from app.blueprints.user import bp as user_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.register_blueprint(user_bp)
    return app