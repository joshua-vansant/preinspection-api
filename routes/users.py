from flask import Blueprint, request, jsonify
from extensions import db
from models import User
from flask_jwt_extended import jwt_required, get_jwt_identity

users_bp = Blueprint("users", __name__)

@users_bp.get("/<int:user_id>")
@jwt_required()
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())

@users_bp.put("/update")
@jwt_required()
def update_user():
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    user.email = data.get("email", user.email)
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.phone_number = data.get("phone_number", user.phone_number)
    user.updated_at = db.func.now()

    # Don't allow role changes here
    db.session.commit()

    return jsonify({
        "message": "User updated successfully",
        "user": user.to_dict()
    })

@users_bp.delete("/delete")
@jwt_required()
def delete_user():
    from models import InspectionResult, Vehicle

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    org_id = user.org_id

    if org_id is None:
        # Solo driver → delete inspections and vehicles they created
        InspectionResult.query.filter_by(driver_id=user.id).delete(synchronize_session=False)
        Vehicle.query.filter_by(created_by_user_id=user.id).delete(synchronize_session=False)
    else:
        # Affiliated → keep inspections, reassign to org; vehicles remain but null out created_by_user_id
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
