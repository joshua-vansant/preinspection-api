from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from extensions import db, bcrypt
from models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.post('/auth/register')
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

@auth_bp.post('/auth/login')
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
    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    print("user.id type after:", type(user.id))
    return jsonify({"access_token": access_token}), 200
