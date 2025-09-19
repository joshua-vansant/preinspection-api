# import os
# import psycopg2
# from dotenv import load_dotenv
# from flask import Flask, jsonify, request
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flask_bcrypt import Bcrypt
# from flask_jwt_extended import JWTManager, create_access_token
# # from models.user import User
from flask import Flask, jsonify
import os
from extensions import db, migrate, bcrypt, jwt
from dotenv import load_dotenv

load_dotenv()
# jwt = JWTManager()

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
    
    
    @app.route('/')
    def index():
        return jsonify({"message": "Welcome to the Pre-Inspection API!"})
    
    return app

app = create_app()