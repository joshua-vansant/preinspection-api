from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from extensions import db, bcrypt
from models.user import User
import re

auth_bp = Blueprint("auth", __name__)

def is_valid_email(email: str) -> bool:
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

@auth_bp.post('/register')
def register():
    data = request.get_json()
    email = data.get('email').strip().lower()
    password = data.get('password')
    first_name = data.get('first_name').strip()
    last_name = data.get('last_name').strip()
    role = data.get('role', 'driver') # default role is driver

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    if not first_name or not last_name:
        return jsonify({"error": "First and Last Names are required"})

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(
        email=email,
        password_hash=password_hash,
        role="driver", 
        first_name=first_name, 
        last_name=last_name, 
        phone_number=data.get('phone_number')
     )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user": new_user.to_dict()
    }), 201


@auth_bp.post('/login')
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", '')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role},
        expires_delta=False  # let config handle expiry
    )
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 3600,
        "user": user.to_dict()
    }), 200


@auth_bp.post('/refresh')
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({"access_token": new_access_token, "expires_in": 3600}), 200