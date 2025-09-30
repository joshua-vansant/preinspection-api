from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.inspection_results import InspectionResult
from models.template import Template
from models.vehicle import Vehicle
from models.user import User
from extensions import db, socketio
from datetime import datetime, timezone

inspections_bp = Blueprint("inspections", __name__)

def driver_can_access(user, inspection):
    if inspection.driver_id == user.id:
        return True
    if user.org_id and inspection.template and inspection.template.org_id == user.org_id:
        return True
    return False
# -----------------------------
# Submit inspection
# -----------------------------
@inspections_bp.post('/submit')
@jwt_required()
def submit_inspection():
    data = request.get_json()
    driver_id = get_jwt_identity()
    template_id = data.get('template_id')
    vehicle_id = data.get('vehicle_id')
    inspection_type = data.get('type')
    results = data.get('results')
    notes = data.get('notes')
    start_mileage = data.get("start_mileage")


    if not template_id or not results or not vehicle_id or not inspection_type:
        return jsonify({"error": "template_id, vehicle_id, type, and results are required"}), 400
    if not isinstance(results, dict):
        return jsonify({"error": "results must be a JSON object"}), 400
    if start_mileage is None:
        return jsonify({"error": "start_mileage is required for all inspections"}), 400
    if start_mileage > 1000000:
        return jsonify({"error": "start_mileage seems too high"}), 400


    claims = get_jwt()
    if claims.get("role") != "driver":
        return jsonify({"error": "Only drivers can submit inspections"}), 403

    template = Template.query.get(template_id)
    if not template:
        return jsonify({"error": "Template not found"}), 404

    driver = User.query.get(driver_id)
    if template.org_id is not None and driver.org_id != template.org_id:
        return jsonify({"error": "Template does not belong to your organization"}), 403

    # --- Mileage validation ---
    vehicle = Vehicle.query.get(vehicle_id)
    if vehicle:
        if vehicle.mileage is not None:
            if start_mileage < vehicle.mileage:
                return jsonify({"error": "start_mileage cannot be less than vehicle's current mileage"}), 400
        else:
            print(f"[DEBUG] Vehicle {vehicle.id} has no mileage set, accepting {start_mileage} as first value.")

    inspection_record = InspectionResult(
        driver_id=driver_id,
        vehicle_id=vehicle_id,
        template_id=template_id,
        type=inspection_type,
        results=results,
        created_at=datetime.now(timezone.utc),
        notes=notes,
        start_mileage=start_mileage,
        fuel_level=data.get("fuel_level"),
        fuel_notes=data.get("fuel_notes"),
        odometer_verified=data.get("odometer_verified", False),
    )

    db.session.add(inspection_record)

    # --- Update vehicle current mileage ---
    if vehicle:
        vehicle.mileage = start_mileage

    db.session.commit()

    # Socket emit
    if driver.org_id:
        socketio.emit(
            "inspection_created",
            {
                **inspection_record.to_dict(),
                "driver": {
                    "id": driver.id,
                    "first_name": driver.first_name,
                    "last_name": driver.last_name,
                    "full_name": f"{driver.first_name} {driver.last_name}"
                }
            },
            room=f"org_{driver.org_id}",
        )

    return jsonify(inspection_record.to_dict()), 201



# -----------------------------
# Get inspection history
# -----------------------------
@inspections_bp.get('/history')
@jwt_required()
def get_inspection_history():
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")
    user = User.query.get(user_id)

    if role == "driver":
        inspections = InspectionResult.query.filter_by(driver_id=user.id).all()


    elif role == "admin":
        if not user.org_id:
            return jsonify({"error": "Admin has no org"}), 400

        # Get all drivers in this org
        org_driver_ids = [id for (id,) in db.session.query(User.id).filter_by(org_id=user.org_id)]
        inspections = InspectionResult.query.filter(
            InspectionResult.driver_id.in_(org_driver_ids)
        ).all()

    else:
        return jsonify({"error": "Unauthorized role"}), 403

    # Build response with driver info
    response = []
    for i in inspections:
        item = i.to_dict()
        if i.driver:
            item["driver"] = {
                "id": i.driver.id,
                "first_name": i.driver.first_name,
                "last_name": i.driver.last_name,
                "full_name": f"{i.driver.first_name} {i.driver.last_name}"
            }
        else:
            item["driver"] = None
        response.append(item)

    return jsonify(response), 200


# -----------------------------
# Get single inspection
# -----------------------------
@inspections_bp.get('/<int:inspection_id>')
@jwt_required()
def get_inspection(inspection_id):
    inspection = InspectionResult.query.get(inspection_id)
    if not inspection:
        return jsonify({"error": "Inspection not found"}), 404

    user = User.query.get(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    if role == "driver" and not driver_can_access(user, inspection):
        return jsonify({"error": "Unauthorized"}), 403

    template = Template.query.get(inspection.template_id)
    response = inspection.to_dict()
    response["template"] = template.to_dict() if template else None
    return jsonify(response), 200


# -----------------------------
# Get last inspection for a vehicle
# -----------------------------
@inspections_bp.get('/last/<int:vehicle_id>')
@jwt_required()
def get_last_inspection(vehicle_id):
    try:
        last_inspection = (
            InspectionResult.query
            .filter_by(vehicle_id=vehicle_id)
            .order_by(InspectionResult.created_at.desc())
            .first()
        )
        if not last_inspection:
            return jsonify({"message": "No inspections found for this vehicle"}), 200

        user = User.query.get(get_jwt_identity())
        claims = get_jwt()
        role = claims.get("role")

        if role == "driver" and not driver_can_access(user, last_inspection):
            return jsonify({"error": "Unauthorized"}), 403

        return jsonify(last_inspection.to_dict()), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


# -----------------------------
# Get inspections for a vehicle
# -----------------------------
@inspections_bp.get('/vehicle/<int:vehicle_id>')
@jwt_required()
def get_vehicle_inspections(vehicle_id):
    user = User.query.get(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    query = InspectionResult.query.filter_by(vehicle_id=vehicle_id).order_by(InspectionResult.created_at.desc())

    if role == "driver":
        if user.org_id:
            template_ids = db.session.query(Template.id).filter_by(org_id=user.org_id)
            query = query.filter(InspectionResult.template_id.in_(template_ids))
        else:
            query = query.filter_by(driver_id=user.id)

    inspections = query.all()
    return jsonify([i.to_dict() for i in inspections]), 200


# -----------------------------
# Update inspection
# -----------------------------
@inspections_bp.put('/<int:inspection_id>')
@jwt_required()
def update_inspection(inspection_id):
    inspection = InspectionResult.query.get(inspection_id)
    if not inspection:
        return jsonify({"error": "Inspection not found"}), 404

    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    if role == "driver" and inspection.driver_id != user_id:
        return jsonify({"error": "Drivers can only edit their own inspections"}), 403
    if role == "driver" and (datetime.utcnow() - inspection.created_at).total_seconds() > 1800:
        return jsonify({"error": "Inspection can no longer be edited"}), 403

    data = request.get_json()
    results = data.get("results")
    notes = data.get("notes")
    start_mileage = data.get("start_mileage")

    if start_mileage is None:
        return jsonify({"error": "start_mileage is required"}), 400

    # --- Mileage validation ---
    vehicle = Vehicle.query.get(inspection.vehicle_id)
    if vehicle and vehicle.mileage is not None:
        if start_mileage < vehicle.mileage:
            return jsonify({"error": "start_mileage cannot be less than vehicle's current mileage"}), 400

    inspection.start_mileage = start_mileage
    inspection.fuel_level = data.get("fuel_level")
    inspection.fuel_notes = data.get("fuel_notes")
    inspection.odometer_verified = data.get("odometer_verified", inspection.odometer_verified)

    if results and not isinstance(results, dict):
        return jsonify({"error": "results must be a JSON object"}), 400
    if results:
        inspection.results = results
    if notes is not None:
        inspection.notes = notes

    # Update vehicle mileage
    if vehicle:
        vehicle.mileage = start_mileage

    db.session.commit()
    return jsonify(inspection.to_dict()), 200
