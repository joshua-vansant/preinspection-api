from flask import Flask, jsonify, request
import os
from extensions import db, migrate, bcrypt, jwt
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token
from models.user import User
from models.template import Template
from models.inspection_results import InspectionResult
from models.template_item import TemplateItem

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
    
    
    @app.get('/')
    def index():
        return jsonify({"message": "Welcome to the Pre-Inspection API!"})

    @app.post('/auth/register')
    def register():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'driver') # default role is driver

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 400

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(email=email, password_hash=password_hash, role=role)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201

    @app.post('/auth/login')
    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = User.query.filter_by(email=email).first()
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid credentials"}), 401

        access_token = create_access_token(identity={"id": user.id, "role": user.role})
        return jsonify({"access_token": access_token}), 200

    @app.get('/inspection_results')
    def get_inspection_results():
        results = InspectionResult.query.all()
        return jsonify([result.to_dict() for result in results]), 200

    @app.post('/inspection_results')
    def create_inspection_result():
        data = request.get_json()
        driver_id = data.get('driver_id')
        template_id = data.get('template_id')
        results = data.get('results')

        if not driver_id or not template_id or not results:
            return jsonify({"error": "Driver ID, template ID, and results are required"}), 400

        new_result = InspectionResult(driver_id=driver_id, template_id=template_id, results=results)
        db.session.add(new_result)
        db.session.commit()

        return jsonify({"message": "Inspection result created successfully"}), 201


    return app

app = create_app()