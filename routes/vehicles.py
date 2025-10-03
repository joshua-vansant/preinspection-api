from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models.vehicle import Vehicle
from models.user import User

vehicles_bp = Blueprint("vehicles", __name__)

# -----------------------------
# GET all vehicles that user can see
# -----------------------------
@vehicles_bp.get('/')
@jwt_required()
def get_vehicles():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    claims = get_jwt()
    role = claims.get("role")

    if not user:
        return jsonify({"error": "User not found"}), 404

    query = Vehicle.query

    if role == "driver":
        if user.org_id:
            query = query.filter(Vehicle.org_id == user.org_id)
        else:
            # Driver with no org sees only vehicles they created
            query = query.filter(Vehicle.org_id.is_(None), Vehicle.created_by_user_id == user.id)
    elif role == "admin":
        if user.org_id:
            query = query.filter(Vehicle.org_id == user.org_id)
        else:
            return jsonify({"error": "Admin has no org"}), 400
    else:
        return jsonify({"error": "Unauthorized role"}), 403

    vehicles = query.order_by(Vehicle.id.desc()).all()
    return jsonify([v.to_dict() for v in vehicles]), 200


# -----------------------------
# POST add a vehicle
# -----------------------------
@vehicles_bp.post('/add')
@jwt_required()
def add_vehicle():
    data = request.get_json()
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    license_plate = data.get('license_plate')
    if not license_plate:
        return jsonify({"error": "License Plate Number is required"}), 400

    number = data.get('number')

    # Determine org_id
    org_id = None
    if role == "admin":
        org_id = data.get("org_id")
        if not org_id:
            return jsonify({"error": "Admin must provide org_id"}), 400
    else:
        org_id = user.org_id  # driver cannot set org_id

    new_vehicle = Vehicle(
        org_id=org_id,
        number=number,
        make=data.get("make"),
        model=data.get("model"),
        year=data.get("year"),
        vin=data.get("vin"),
        license_plate=license_plate,
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


# -----------------------------
# PUT/PATCH update a vehicle (admin-only)
# -----------------------------
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


# -----------------------------
# DELETE a vehicle (admin-only)
# -----------------------------
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
