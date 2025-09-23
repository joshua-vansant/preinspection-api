from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models.vehicle import Vehicle
from models.user import User

vehicles_bp = Blueprint("vehicles", __name__)

# GET all vehicles for user's org
@vehicles_bp.get('/')
@jwt_required()
def get_vehicles():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    vehicles = Vehicle.query.filter_by(org_id=user.org_id).all()

    return jsonify([{
        "id": v.id,
        "org_id": v.org_id,
        "number": v.number
    } for v in vehicles]), 200


# POST add a vehicle
@vehicles_bp.post('/add')
@jwt_required()
def add_vehicle():
    data = request.get_json()
    user_id = get_jwt_identity()
    claims = get_jwt()
    user = User.query.get(user_id)

    number = data.get('number')
    if not number:
        return jsonify({"error": "Vehicle number is required"}), 400

    # Determine org_id
    org_id = data.get('org_id')
    if claims.get("role") == "admin":
        if not org_id:
            return jsonify({"error": "Admin must provide org_id"}), 400
    else:
        # driver cannot set org_id, use their own org
        org_id = user.org_id

    new_vehicle = Vehicle(org_id=org_id, number=number)
    db.session.add(new_vehicle)
    db.session.commit()

    return jsonify({
        "id": new_vehicle.id,
        "org_id": new_vehicle.org_id,
        "number": new_vehicle.number
    }), 201


# PUT/PATCH update a vehicle (admin-only)
@vehicles_bp.put('/<int:vehicle_id>')
@vehicles_bp.patch('/<int:vehicle_id>')
@jwt_required()
def update_vehicle(vehicle_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Only admins can update vehicles"}), 403

    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    data = request.get_json()
    vehicle.org_id = data.get('org_id', vehicle.org_id)
    vehicle.number = data.get('number', vehicle.number)

    db.session.commit()

    return jsonify({
        "id": vehicle.id,
        "org_id": vehicle.org_id,
        "number": vehicle.number
    }), 200


# DELETE a vehicle (admin-only)
@vehicles_bp.delete('/<int:vehicle_id>')
@jwt_required()
def delete_vehicle(vehicle_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Only admins can delete vehicles"}), 403

    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({"message": "Vehicle deleted successfully"}), 200
    