from flask import Flask, jsonify, request
import os
from extensions import db, migrate, bcrypt, jwt
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token, jwt_required
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

        print("user.id type before:", type(user.id))
        # access_token = create_access_token(identity={"id": str(user.id), "role": user.role})
        access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
        print("user.id type after:", type(user.id))
        return jsonify({"access_token": access_token}), 200

    @app.get('/templates')
    @jwt_required()
    def get_templates():
        #Get current user
        current_user_id = jwt.get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        #Always fetch the default template
        templates = Template.query.filter(Template.is_default == True).all()

        #If user is in an org, get org templates
        if user.org_id:
            org_templates = Template.query.filter(Template.created_by == user.org_id).all()
            templates.extend(org_templates)

        #Serialize templates
        templates_data = []
        for template in templates:
            items = TemplateItem.query.filter_by(template_id=template.id).all()
            templates_data.append({
                "id": template.id,
                "name": template.name,
                "created_by": template.created_by,
                "created_at": template.created_at,
                "is_default": template.is_default,
                "items": [{"id": item.id, "name": item.name, "question": item.question} for item in items]
            })

        return jsonify(templates_data), 200

    return app
app = create_app()