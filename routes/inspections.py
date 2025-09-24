from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.inspection_results import InspectionResult
from models.template import Template
from models.vehicle import Vehicle
from extensions import db, bcrypt
from models.user import User
from datetime import datetime, timezone

inspections_bp = Blueprint("inspections", __name__)

@inspections_bp.post('/submit')
@jwt_required()
def submit_inspection():
    data = request.get_json()
    driver_id = get_jwt_identity()
    template_id = data.get('template_id')
    vehicle_id = data.get('vehicle_id')
    inspection_type = data.get('type')  # 'pre' or 'post'
    results = data.get('results')
    notes = data.get('notes')

    if not template_id or not results or not vehicle_id or not inspection_type:
        return jsonify({"error": "template_id, vehicle_id, type, and results are required"}), 400

    if not isinstance(results, dict):
        return jsonify({"error": "results must be a JSON object"}), 400

    claims = get_jwt()
    if claims.get("role") != "driver":
        return jsonify({"error": "Only drivers can submit inspections"}), 403

    template = Template.query.get(template_id)
    if not template:
        return jsonify({"error": "Template not found"}), 404

    driver = User.query.get(driver_id)
    if driver.org_id != template.org_id:
        return jsonify({"error": "Template does not belong to your organization"}), 403

    # For post-inspections, fetch last inspection on the vehicle
    previous_data = {}
    if inspection_type == 'post':
        last_inspection = (
            InspectionResult.query
            .filter_by(vehicle_id=vehicle_id)
            .order_by(InspectionResult.created_at.desc())
            .first()
        )
        if last_inspection:
            previous_data = {
                "gas_level": last_inspection.results.get("gas_level"),
                "odometer": last_inspection.results.get("odometer")
            }

    # Create the inspection record
    inspection_record = InspectionResult(
        driver_id=driver_id,
        vehicle_id=vehicle_id,
        template_id=template_id,
        type=inspection_type,
        results=results,
        created_at=datetime.now(timezone.utc),
        notes=notes
    )

    db.session.add(inspection_record)
    db.session.commit()

    response = {
        "id": inspection_record.id,
        "driver_id": inspection_record.driver_id,
        "vehicle_id": inspection_record.vehicle_id,
        "template_id": inspection_record.template_id,
        "type": inspection_record.type,
        "results": inspection_record.results,
        "created_at": inspection_record.created_at.isoformat() +"Z",
        "notes": inspection_record.notes
    }

    if previous_data:
        response["previous"] = previous_data

    return jsonify(response), 201


@inspections_bp.get('/history')
@jwt_required()
def get_inspection_history():
    claims = get_jwt()
    role = claims.get("role")
    user_id = get_jwt_identity()

    if role == "driver":
        # Driver can only see their own inspections
        inspections = InspectionResult.query.filter_by(driver_id=user_id).all()
    elif role == "admin":
        # get all users in this admin's org
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Admin user not found"}), 404
        # org_driver_ids = [u.id for u in User.query.filter_by(org_id=user.org_id).all()]
        # inspections = InspectionResult.query.filter(InspectionResult.driver_id.in_(org_driver_ids)).all()
        org_driver_ids = db.session.query(User.id).filter_by(org_id=user.org_id)
        inspections = InspectionResult.query.filter(InspectionResult.driver_id.in_(org_driver_ids)).all()

    else:
        return jsonify({"error": "Unauthorized role"}), 403

    return jsonify([{
        "id": inspection.id,
        "driver_id": inspection.driver_id,
        "template_id": inspection.template_id,
        "results": inspection.results,
        "created_at": inspection.created_at.isoformat()
    } for inspection in inspections]), 200

    
@inspections_bp.get('/last/<int:vehicle_id>')
@jwt_required()
def get_last_inspection(vehicle_id):
    claims = get_jwt()
    role = claims.get("role")
    user_id = get_jwt_identity()

    # Drivers can only access vehicles in their org
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Grab the last inspection for this vehicle
    last_inspection = (
        InspectionResult.query
        .filter_by(vehicle_id=vehicle_id)
        .order_by(InspectionResult.created_at.desc())
        .first()
    )

    if not last_inspection:
        return jsonify({"message": "No inspections found for this vehicle"}), 200

    # Optional: if driver role, ensure inspection belongs to same org
    if role == "driver":
        template = Template.query.get(last_inspection.template_id)
        if template.org_id != user.org_id:
            return jsonify({"error": "Unauthorized"}), 403

    response = {
        "id": last_inspection.id,
        "driver_id": last_inspection.driver_id,
        "vehicle_id": last_inspection.vehicle_id,
        "template_id": last_inspection.template_id,
        "type": last_inspection.type,
        "results": last_inspection.results,
        "created_at": last_inspection.created_at.isoformat(),
        "notes": last_inspection.notes
    }

    return jsonify(response), 200


@inspections_bp.get('/vehicle/<int:vehicle_id>')
@jwt_required()
def get_vehicle_inspections(vehicle_id):
    claims = get_jwt()
    role = claims.get("role")
    user_id = get_jwt_identity()

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    query = InspectionResult.query.filter_by(vehicle_id=vehicle_id).order_by(InspectionResult.created_at.desc())

    # Restrict drivers to only their org
    if role == "driver":
        template_ids = db.session.query(Template.id).filter_by(org_id=user.org_id)
        query = query.filter(InspectionResult.template_id.in_(template_ids))

    inspections = query.all()

    return jsonify([{
        "id": i.id,
        "driver_id": i.driver_id,
        "vehicle_id": i.vehicle_id,
        "template_id": i.template_id,
        "type": i.type,
        "results": i.results,
        "created_at": i.created_at.isoformat(),
        "notes": i.notes
    } for i in inspections]), 200


@inspections_bp.put('/<int:inspection_id>')
@jwt_required()
def update_inspection(inspection_id):
    claims = get_jwt()
    role = claims.get("role")
    user_id = get_jwt_identity()

    inspection = InspectionResult.query.get(inspection_id)
    if not inspection:
        return jsonify({"error": "Inspection not found"}), 404

    print("JWT driver_id:", get_jwt_identity())
    print("Inspection driver_id:", inspection.driver_id)


    if role == "driver" and int(inspection.driver_id) != int(user_id):
        return jsonify({"error": "Drivers can only edit their own inspections"}), 403

    # Drivers can edit their own results within 30 minuts
    if role == "driver" and (datetime.utcnow() - inspection.created_at).total_seconds() > 1800:
        return jsonify({"error": "Inspection can no longer be edited"}), 403

    data = request.get_json()
    results = data.get("results")
    notes = data.get("notes")

    if results and not isinstance(results, dict):
        return jsonify({"error": "results must be a JSON object"}), 400

    if results:
        inspection.results = results
    if notes is not None:
        inspection.notes = notes

    db.session.commit()

    return jsonify({
        "id": inspection.id,
        "driver_id": inspection.driver_id,
        "vehicle_id": inspection.vehicle_id,
        "template_id": inspection.template_id,
        "type": inspection.type,
        "results": inspection.results,
        "created_at": inspection.created_at.isoformat(),
        "notes": inspection.notes
    }), 200



@inspections_bp.get('/vehicle/<int:vehicle_id>/status')
@jwt_required()
def get_vehicle_status(vehicle_id):
    claims = get_jwt()
    role = claims.get("role")
    user_id = get_jwt_identity()

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    # Get last inspection of any type
    last_inspection = (
        InspectionResult.query
        .filter_by(vehicle_id=vehicle_id)
        .order_by(InspectionResult.created_at.desc())
        .first()
    )

    if not last_inspection:
        return jsonify({
            "vehicle_id": vehicle.id,
            "status": "No inspections yet"
        }), 200

    # Drivers can only see vehicles in their org
    if role == "driver":
        template = Template.query.get(last_inspection.template_id)
        if template.org_id != user.org_id:
            return jsonify({"error": "Unauthorized"}), 403

    response = {
        "vehicle_id": vehicle.id,
        "vehicle_name": getattr(vehicle, "name", None),
        "last_inspection": {
            "id": last_inspection.id,
            "type": last_inspection.type,
            "results": last_inspection.results,
            "created_at": last_inspection.created_at.isoformat(),
            "notes": last_inspection.notes
        }
    }

    return jsonify(response), 200


@inspections_bp.get('/templates/available')
@jwt_required()
def get_available_templates():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    templates = Template.query.filter_by(org_id=user.org_id).all()

    return jsonify([{
        "id": t.id,
        "name": t.name,
        "org_id": t.org_id,
        "created_at": t.created_at,
        "is_default": t.is_default
    } for t in templates]), 200