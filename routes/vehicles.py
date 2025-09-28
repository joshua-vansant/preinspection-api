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
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.org_id:
        # User belongs to an org — return all vehicles for that org
        vehicles = Vehicle.query.filter_by(org_id=user.org_id).all()
    else:
        # User does not belong to an org — return only vehicles they created
        vehicles = Vehicle.query.filter_by(org_id=None, created_by_user_id=user_id).all()

    return jsonify([v.to_dict() for v in vehicles]), 200


# POST add a vehicle
@vehicles_bp.post('/add')
@jwt_required()
def add_vehicle():
    data = request.get_json()
    user_id = get_jwt_identity()
    claims = get_jwt()
    user = User.query.get(user_id)

    # number = data.get('number')
    # if not number:
    #     return jsonify({"error": "Vehicle number is required"}), 400

    license_plate = data.get('license_plate')
    if not license_plate:
        return jsonify({"error": "License Plate Number is required"}), 400
    

    # Determine org_id
    org_id = data.get('org_id')
    if claims.get("role") == "admin":
        if not org_id:
            return jsonify({"error": "Admin must provide org_id"}), 400
    else:
        # driver cannot set org_id, use their own org (might be None)
        org_id = user.org_id

    new_vehicle = Vehicle(
        org_id=org_id,
        number=number,
        make=data.get("make"),
        model=data.get("model"),
        year=data.get("year"),
        vin=data.get("vin"),
        license_plate=data.get("license_plate"),
        mileage=data.get("mileage"),
        status=data.get("status", "active"),
        created_by_user_id=user_id,
    )

    db.session.add(new_vehicle)
    db.session.commit()

    return jsonify({
        "message": "Vehicle added successfully",
        "vehicle": new_vehicle.to_dict()
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
    vehicle.make = data.get('make', vehicle.make)
    vehicle.model = data.get('model', vehicle.model)
    vehicle.year = data.get('year', vehicle.year)
    vehicle.vin = data.get('vin', vehicle.vin)
    vehicle.license_plate = data.get('license_plate', vehicle.license_plate)
    vehicle.mileage = data.get('mileage', vehicle.mileage)
    vehicle.status = data.get('status', vehicle.status)

    db.session.commit()

    return jsonify({
        "message": "Vehicle updated successfully",
        "vehicle": vehicle.to_dict() 
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
