from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models.organization import Organization
from models.user import User

import uuid

organizations_bp = Blueprint("organizations", __name__)

@organizations_bp.get('/code')
@jwt_required()
def get_organization_code():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or user.role != 'admin':
        return jsonify({"error": "User not found or not authorized"}), 403

    org = Organization.query.get(user.org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    return jsonify({"invite_code": org.invite_code}), 200


@organizations_bp.post('/join')
@jwt_required()
def join_organization():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or user.role != 'driver':
        return jsonify({"error": "Only drivers can join an organization."}), 403

    data = request.get_json()
    invite_code = data.get("invite_code")

    if not invite_code:
        return jsonify({"error": "Invite code is required"}), 400

    org = Organization.query.filter_by(invite_code=invite_code).first()
    if not org:
        return jsonify({"error": "Invalid invite code"}), 404

    user.org_id = org.id
    db.session.commit()

    return jsonify({"message": f"Driver {user.id} successfully joined {org.name}"}), 200
    

@organizations_bp.post("/create")
@jwt_required()
def create_organization():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or user.role != "admin":
        return jsonify({"error": "Only admins can create organizations"}), 403

    if user.org_id:
        return jsonify({"error": "User already belongs to an organization"}), 400

    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Organization name is required"}), 400

    new_org = Organization(
        name=name,
        admin_id=user.id
    )

    db.session.add(new_org)
    db.session.commit()

    # Assign org_id to admin
    user.org_id = new_org.id
    db.session.commit()

    return jsonify({
        "message": "Organization created successfully",
        "id": new_org.id,
        "invite_code": new_org.invite_code
    }), 201
