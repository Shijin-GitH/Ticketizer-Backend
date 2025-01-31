from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    Migrate(app,db)

    with app.app_context():
        from app.routes import bp
        from app.blueprints.user import bp as user_bp
        app.register_blueprint(bp)
        app.register_blueprint(user_bp)
        db.create_all()

    return app