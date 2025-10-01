from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db, bcrypt
from models.user import User
import re
from models.organization import Organization
import secrets

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
        "user": new_admin.to_dict()
    }), 201


@admins_bp.post('/invite')
@jwt_required()
def generate_admin_invite():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"error": "Only admins can generate admin invites"}), 403

    # Generate a unique, random code
    code = secrets.token_urlsafe(8)

    org = Organization.query.get(user.org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404
    org.admin_invite_code = db.session.add(new_invite)
    
    db.session.commit()

    return jsonify({"code": code}), 201


@admins_bp.post('/redeem')
@jwt_required()
def redeem_admin_invite():
    current_app.logger.debug("redeem_admin_invite() called")
    current_app.logger.debug(f"JWT identity: {get_jwt_identity()}")
    current_app.logger.debug(f"Request JSON: {request.get_json()}")
    user = User.query.get(get_jwt_identity())
    data = request.get_json()
    code = data.get("code", "").strip()
    print(f"Received code from client: '{code}'")

    if not code:
        return jsonify({"error": "Code is required"}), 400

    org = Organization.query.filter_by(admin_invite_code=code).first()
    print(f"Looking for org with admin_invite_code='{code}', found: {org}")  # DEBUG

    if not org:
        return jsonify({"error": "Invalid code"}), 400

    # Update role
    user.role = "admin"
    user.org_id = org.id

    # Optional: invalidate the code
    org.admin_invite_code = None
    db.session.commit()

    return jsonify({"message": "You are now an admin", "org_id": org.id}), 200


def is_valid_email(email: str) -> bool:
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None
