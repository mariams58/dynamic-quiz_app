from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_session import Session

# Initialize extentions
db = SQLAlchemy()
session = Session()

# Create function for Flask app
def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    #Initialize extentions
    db.init_app(app)
    session.init_app(app)
    CORS(app)

    #Resgister the blueprints
    from app.routes.auth import auth_bp
    from app.routes.quiz import quiz_bp
    from app.routes.admin import admin_bp
    app.register_blueprint(auth_bp, url_prfix='/auth')
    app.register_blueprint(quiz_bp, url_prfix='/quiz')
    app.register_blueprint(admin_bp, url_prfix='/admin')

    with app.app_context():
        db.create_all()
    
    return app
