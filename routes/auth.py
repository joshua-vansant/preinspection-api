from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from extensions import db, bcrypt
from models.user import User
from models.password_reset_token import PasswordResetToken
import re
import uuid
from datetime import datetime, timedelta

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

    access_token = create_access_token(
        identity=str(new_user.id),
        additional_claims={"role": new_user.role}
    )
    refresh_token = create_refresh_token(identity=str(new_user.id))

    return jsonify({
        "message": "User registered successfully",
        "user": new_user.to_dict(include_org=False),
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 3600
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

    # Dynamic role: driver if not in org
    role = 'driver' if not user.org_id else user.role

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": role},
        expires_delta=False
    )
    refresh_token = create_refresh_token(identity=str(user.id))

    user_dict = user.to_dict()
    user_dict['role'] = role 

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 3600,
        "user": user_dict
    }), 200


@auth_bp.post('/refresh')
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({"access_token": new_access_token, "expires_in": 3600}), 200


@auth_bp.post("/request-password-reset")
def request_password_reset():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "If an account exists, a reset link has been sent."}), 200

    PasswordResetToken.query.filter_by(user_id=user.id).delete()

    token = str(uuid.uuid4())
    expires_at = datetime.utcnow().replace(microsecond=0) + timedelta(minutes=30)
    reset_entry = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )

    db.session.add(reset_entry)
    db.session.commit()

    return jsonify({
        "message": "Password reset requested. Use the token to reset your password.",
        "reset_token": token,
        "expires_at": expires_at.isoformat() + "Z"
    }), 200


@auth_bp.post("/reset-password")
def reset_password():
    data = request.get_json() or {}
    token = data.get("token")
    new_password = data.get("new_password")

    if not token or not new_password:
        return jsonify({"error": "Token and new password are required"}), 400

    reset_entry = PasswordResetToken.query.filter_by(token=token).first()

    if not reset_entry:
        return jsonify({"error": "Invalid or expired token"}), 400

    if reset_entry.expires_at < datetime.utcnow():
        db.session.delete(reset_entry)
        db.session.commit()
        return jsonify({"error": "Token has expired"}), 400

    user = User.query.get(reset_entry.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
    db.session.delete(reset_entry)
    db.session.commit()

    return jsonify({"message": "Password reset successful"}), 200