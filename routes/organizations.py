from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models.organization import Organization
from models.user import User
from models.vehicle import Vehicle
from sockets.org_events import notify_driver_joined, notify_driver_left
from uuid import uuid4

organizations_bp = Blueprint("organizations", __name__)

@organizations_bp.get('/code')
@jwt_required()
def get_organization_code():
    user = User.query.get(get_jwt_identity())
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

    return jsonify(org.to_dict()), 200

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
    users_data = [u.to_dict() for u in users]  # ✅ use to_dict()

    return jsonify({"organization": org.to_dict(), "users": users_data}), 200

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
    user = User.query.get(get_jwt_identity())
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
    db.session.commit()
    notify_driver_joined(user.org_id, user)

    return jsonify({
        "message": f"Driver {user.id} successfully joined {org.name}",
        "organization": org.to_dict()
    }), 200

@organizations_bp.post("/create")
@jwt_required()
def create_organization():
    user = User.query.get(get_jwt_identity())

    # Ensure user is not already in an org
    if user.org_id:
        return jsonify({"error": "User already belongs to an organization"}), 400


    data = request.get_json()
    name = data.get("name").strip()

    # Validation for org name...
    if Organization.query.filter_by(name=name).first():
        return jsonify({"error": "Organization already exists"}), 400

    # Create new org
    new_org = Organization(name=name, admin_id=user.id)
    db.session.add(new_org)
    db.session.commit()

    user.org_id = new_org.id
    if user.role == "driver":
        user.role = "admin"
    db.session.commit()


    return jsonify({
        "message": "Organization created successfully",
        "organization": new_org.to_dict()
    }), 201


@organizations_bp.delete("/delete")
@jwt_required()
def delete_organization():
    user = User.query.get(get_jwt_identity())
    if not user or user.role != "admin":
        return jsonify({"error": "Only admins can delete organizations"}), 403

    org = Organization.query.get(user.org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    # Remove vehicles
    for vehicle in Vehicle.query.filter_by(org_id=org.id).all():
        if vehicle.created_by_user_id is None:
            db.session.delete(vehicle)
        else:
            vehicle.org_id = None


    # Remove templates but keep inspections
    for template in org.templates:
        # Detach inspections from template
        for inspection in template.inspections:
            inspection.template_id = None
        db.session.delete(template)

    # remove invite codes
    org.invite_code = None
    org.admin_invite_code = None

    # Remove org reference from users
    users = User.query.filter_by(org_id=org.id).all()
    for u in users:
        u.org_id = None
        if u.role == "admin":
            u.role = "driver"

    db.session.delete(org)
    db.session.commit()

    return jsonify({"message": "Organization deleted, inspections retained"}), 200


@organizations_bp.put('/<int:org_id>')
@jwt_required()
def update_organization(org_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    org = Organization.query.get(org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    if org.id != user.org_id:
        return jsonify({"error": "Cannot edit this organization"}), 403

    data = request.get_json()
    if 'name' in data and data['name']:
        org.name = data['name'].strip()
    if 'address' in data:
        org.address = data['address'].strip() if data['address'] else None
    if 'phone_number' in data:
        org.phone_number = data['phone_number'].strip() if data['phone_number'] else None
    if 'contact_name' in data:
        org.contact_name = data['contact_name'].strip() if data['contact_name'] else None


    db.session.commit()
    return jsonify(org.to_dict()), 200

@organizations_bp.post("/remove_driver")
@jwt_required()
def remove_driver():
    user = User.query.get(get_jwt_identity())
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
    if driver.id == user.id:
        return jsonify({"error": "Admins cannot remove themselves"}), 400

    driver.org_id = None
    db.session.commit()
    notify_driver_left(user.org_id, driver)

    return jsonify({"message": f"Driver {driver.id} removed from organization"}), 200

@organizations_bp.post("/leave")
@jwt_required()
def leave_organization():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not user.org_id:
        return jsonify({"error": "User is not part of any organization"}), 400
    if user.role == "admin":
        admin_count = User.query.filter_by(org_id=user.org_id, role="admin").count()
        if admin_count <= 1:
            return jsonify({"error": "Cannot leave organization as the sole admin. Please assign another admin before leaving."}), 400

    org_id = user.org_id
    user.org_id = None
    db.session.commit()
    notify_driver_left(org_id, user)

    return jsonify({"message": "Successfully left the organization"}), 200


@organizations_bp.get("/admin_code")
@jwt_required()
def get_admin_invite_code():
    user = User.query.get(get_jwt_identity())
    if not user or user.role != "admin":
        return jsonify({"error": "Only admins can generate admin codes"}), 403

    org = Organization.query.get(user.org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    # Generate if missing
    if not org.admin_invite_code:
        org.admin_invite_code = str(uuid4()).split("-")[0].upper()
        db.session.commit()

    return jsonify({"admin_invite_code": org.admin_invite_code})


@organizations_bp.post("/admin_code/regenerate")
@jwt_required()
def regenerate_admin_code():
    user = User.query.get(get_jwt_identity())
    if not user or user.role != "admin":
        return jsonify({"error": "Only admins can regenerate admin codes"}), 403

    org = Organization.query.get(user.org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    org.admin_invite_code = str(uuid4()).split("-")[0].upper()
    db.session.commit()
    return jsonify({"admin_invite_code": org.admin_invite_code})
