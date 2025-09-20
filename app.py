from flask import Flask, jsonify, request
from extensions import db, migrate, bcrypt, jwt
from routes.auth import auth_bp
from routes.templates import templates_bp
from routes.inspections import inspections_bp
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Load configuration from environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(templates_bp, url_prefix="/templates")
    app.register_blueprint(inspections_bp, url_prefix="/inspections")

    
    
    @app.get('/')
    def index():
        return jsonify({"message": "Welcome to the Pre-Inspection API!"})


    return app
app = create_app()