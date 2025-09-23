from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.inspection_results import InspectionResult
from models.template import Template
from extensions import db, bcrypt
from models.user import User

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
        created_at=db.func.now(),
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
        "created_at": inspection_record.created_at,
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