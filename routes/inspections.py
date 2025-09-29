from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.inspection_results import InspectionResult
from models.template import Template
from models.vehicle import Vehicle
from models.user import User
from extensions import db, socketio
from datetime import datetime, timezone

inspections_bp = Blueprint("inspections", __name__)

# Helper: Check if driver has access to an inspection
def driver_can_access(user, inspection):
    if user.org_id:
        return inspection.template.org_id == user.org_id
    return inspection.driver_id == user.id

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
    # Safe org check
    if template.org_id is not None and driver.org_id != template.org_id:
        return jsonify({"error": "Template does not belong to your organization"}), 403

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

    # Emit socket event to org room (skip if org_id is None)
    if driver.org_id:
        socketio.emit(
            "inspection_created",
            {
                "id": inspection_record.id,
                "driver_id": driver_id,
                "template_id": template_id,
                "created_at": inspection_record.created_at.isoformat(),
            },
            room=f"org_{driver.org_id}",
        )

    response = inspection_record.to_dict()
    if previous_data:
        response["previous"] = previous_data

    return jsonify(response), 201


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
        if user.org_id:
            inspections = (
                db.session.query(InspectionResult)
                .join(Template)
                .filter(Template.org_id == user.org_id)
                .all()
            )
        else:
            inspections = InspectionResult.query.filter_by(driver_id=user.id).all()
    elif role == "admin":
        if not user.org_id:
            return jsonify({"error": "Admin has no org"}), 400
        org_driver_ids = db.session.query(User.id).filter_by(org_id=user.org_id)
        inspections = InspectionResult.query.filter(
            InspectionResult.driver_id.in_(org_driver_ids)
        ).all()
    else:
        return jsonify({"error": "Unauthorized role"}), 403

    return jsonify([
        {
            **i.to_dict(),
            "driver": {
                "id": i.driver.id,
                "name": i.driver.name,
                "email": i.driver.email,
            } if i.driver else None
        }
        for i in inspections
    ]), 200


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

    if results and not isinstance(results, dict):
        return jsonify({"error": "results must be a JSON object"}), 400
    if results:
        inspection.results = results
    if notes is not None:
        inspection.notes = notes

    db.session.commit()
    return jsonify(inspection.to_dict()), 200
