from flask import Blueprint, request, jsonify
from extensions import db
from models import User
from flask_jwt_extended import jwt_required, get_jwt_identity
import re
from sockets.user_events import notify_user_updated

users_bp = Blueprint("users", __name__)

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
PHONE_REGEX = r"^\+?\d{7,15}$"
# @users_bp.get("/<int:user_id>")
# @jwt_required()
# def get_user(user_id):
#     user = User.query.get(user_id)
#     if not user:
#         return jsonify({"error": "User not found"}), 404
#     return jsonify(user.to_dict())

@users_bp.put("/update")
@jwt_required()
def update_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json() or {}
    errors = {}

    # Validate first name
    first_name = data.get("first_name", user.first_name)
    if not isinstance(first_name, str) or not first_name.strip():
        errors["first_name"] = "First name cannot be empty."
    else:
        first_name = first_name.strip()

    # Validate last name
    last_name = data.get("last_name", user.last_name)
    if not isinstance(last_name, str) or not last_name.strip():
        errors["last_name"] = "Last name cannot be empty."
    else:
        last_name = last_name.strip()

    # Validate email
    email = data.get("email", user.email)
    if not isinstance(email, str) or not re.match(EMAIL_REGEX, email):
        errors["email"] = "Invalid email format."
    elif email != user.email and User.query.filter_by(email=email).first():
        errors["email"] = "Email already in use."

    # Validate phone number
    phone_number = data.get("phone_number", user.phone_number)
    if phone_number:
        if not isinstance(phone_number, str) or not re.match(PHONE_REGEX, phone_number):
            errors["phone_number"] = "Invalid phone number format."

    if errors:
        return jsonify({"errors": errors}), 400

    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.phone_number = phone_number
    user.updated_at = db.func.now()

    db.session.commit()
    notify_user_updated(user.org_id, user)

    return jsonify({"message": "User updated successfully", "user": user.to_dict()})
    
@users_bp.delete("/delete")
@jwt_required()
def delete_user():
    from models import InspectionResult, Vehicle

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    org_id = user.org_id

    print(f"Deleting user {user.id}, org_id={org_id}")

    if org_id is None:
        # Solo driver → delete inspections and vehicles they created
        print("Solo driver branch")
        InspectionResult.query.filter_by(driver_id=user.id).delete(synchronize_session=False)
        Vehicle.query.filter_by(created_by_user_id=user.id).delete(synchronize_session=False)
    else:
        # Affiliated → keep inspections, reassign to org; vehicles remain but null out created_by_user_id
        print("Affiliated branch")
        InspectionResult.query.filter_by(driver_id=user.id).update(
            {"driver_id": None, "org_id": org_id}, synchronize_session=False
        )
        Vehicle.query.filter_by(created_by_user_id=user.id).update(
            {"created_by_user_id": None}, synchronize_session=False
        )

    # Delete the user itself
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200
