from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db, bcrypt
from models.user import User
import re

admins_bp = Blueprint("admins", __name__)

@admins_bp.post('/create')
@jwt_required()
def create_admin():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    claims = get_jwt()
    
    if claims.get("role") != "admin":
        return jsonify({"error": "Only admins can create new admins"}), 403

    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_admin = User(email=email, password_hash=password_hash, org_id=user.org_id, role="admin")

    db.session.add(new_admin)
    db.session.commit()

    return jsonify({
        "message": "Admin user created successfully",
        "id": new_admin.id,
        "role": new_admin.role
    }), 201

def is_valid_email(email: str) -> bool:
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None
