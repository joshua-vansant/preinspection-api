from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models.organization import Organization
from models.user import User
from sockets.org_events import notify_driver_joined
import uuid

organizations_bp = Blueprint("organizations", __name__)

@organizations_bp.get('/code')
@jwt_required()
def get_organization_code():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or user.role != 'admin':
        return jsonify({"error": "Only admins can get the organization invite code"}), 403

    org = Organization.query.get(user.org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    return jsonify({"invite_code": org.invite_code}), 200


@organizations_bp.get('/me')
@jwt_required()
def get_my_organization():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.org_id:
        return jsonify({"error": "User does not belong to any organization"}), 404

    org = Organization.query.get(user.org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    return jsonify({
        "id": org.id,
        "name": org.name
    }), 200


@organizations_bp.get('/users')
@jwt_required()
def get_org_users():
    user = User.query.get(get_jwt_identity())
    if not user or user.role != "admin":
        return jsonify({"error": "Only admins can view org users"}), 403

    org = Organization.query.get(user.org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    users = User.query.filter_by(org_id=org.id).all()
    users_data = [
        {"id": u.id, "email": u.email, "role": u.role}
        for u in users
    ]

    return jsonify({"organization": org.name, "users": users_data}), 200


@organizations_bp.post('/code/regenerate')
@jwt_required()
def regenerate_org_code():
    user = User.query.get(get_jwt_identity())
    if not user or user.role != "admin":
        return jsonify({"error": "Only admins can regenerate codes"}), 403

    org = Organization.query.get(user.org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    org.invite_code = str(uuid.uuid4())[:8]
    db.session.commit()

    return jsonify({"invite_code": org.invite_code}), 200


@organizations_bp.post('/join')
@jwt_required()
def join_organization():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or user.role != 'driver':
        return jsonify({"error": "Only drivers can join an organization"}), 403

    data = request.get_json()
    invite_code = data.get("invite_code")

    if not invite_code:
        return jsonify({"error": "Invite code is required"}), 400

    org = Organization.query.filter_by(invite_code=invite_code).first()
    if not org:
        return jsonify({"error": "Invite code not found"}), 404

    user.org_id = org.id
    notify_driver_joined(user.org_id, user)
    db.session.commit()

    return jsonify({
        "message": f"Driver {user.id} successfully joined {org.name}",
        "organization": {"id": org.id, "name": org.name}
    }), 200


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
    
    if not isinstance(name, str) or len(name.strip()) < 3:
        return jsonify({"error": "Organization name must be at least 3 characters"}), 400

    if Organization.query.filter_by(name=name).first():
        return jsonify({"error": "Organization with this name already exists"}), 400


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
        "name": new_org.name,
        "invite_code": new_org.invite_code
    }), 201


@organizations_bp.post("/remove_driver")
@jwt_required()
def remove_driver():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or user.role != "admin":
        return jsonify({"error": "Only admins can remove drivers"}), 403

    data = request.get_json()
    driver_id = data.get("driver_id")

    if not driver_id:
        return jsonify({"error": "driver_id is required"}), 400

    driver = User.query.get(driver_id)
    if not driver or driver.role != "driver":
        return jsonify({"error": "Driver not found"}), 404

    if driver.org_id != user.org_id:
        return jsonify({"error": "Driver does not belong to your organization"}), 403
    
    if driver.id == user.id: #future proofing - admins might be able to be drivers eventually
        return jsonify({"error": "Admins cannot remove themselves"}), 400


    driver.org_id = None
    db.session.commit()

    return jsonify({"message": f"Driver {driver.id} removed from organization"}), 200
    

@organizations_bp.post("/leave")
@jwt_required()
def leave_organization():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.org_id:
        return jsonify({"error": "User is not part of any organization"}), 400

    if user.role == "admin":
        admin_count = User.query.filter_by(org_id=user.org_id, role="admin").count()
        if admin_count <= 1:
            return jsonify({"error": "Cannot leave organization as the sole admin. Please assign another admin before leaving."}), 400

    # All roles can leave
    user.org_id = None
    db.session.commit()

    return jsonify({"message": "Successfully left the organization"}), 200
