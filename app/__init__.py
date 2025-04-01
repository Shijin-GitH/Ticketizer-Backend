from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    Migrate(app,db)
    CORS(app)

    with app.app_context():
        from app.routes import bp
        from app.blueprints.user import bp as user_bp
        from app.blueprints.event import bp as event_bp
        from app.blueprints.ticket import bp as ticket_bp
        from app.blueprints.forms import bp as forms_bp
        from app.blueprints.payment import bp as payment_bp
        
        app.register_blueprint(bp)
        app.register_blueprint(user_bp)
        app.register_blueprint(event_bp)
        app.register_blueprint(ticket_bp)
        app.register_blueprint(forms_bp)
        app.register_blueprint(payment_bp)
        db.create_all()

    return app
