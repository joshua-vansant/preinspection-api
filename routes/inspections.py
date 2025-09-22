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
    # driver_id = data.get('driver_id')
    template_id = data.get('template_id')
    results = data.get('results')
    if not template_id or not results:
        return jsonify({"error": "template_id and results are required"}), 400

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


    inspection_record = InspectionResult(
        driver_id=driver_id,
        template_id=template_id,
        results=results,
        created_at=db.func.now(),
        notes=data.get('notes')
    )

    db.session.add(inspection_record)
    db.session.commit()

    return jsonify({
        "id": inspection_record.id,
        "driver_id": inspection_record.driver_id,
        "template_id": inspection_record.template_id,
        "results": inspection_record.results,
        "created_at": inspection_record.created_at,
        "notes": inspection_record.notes
    }), 201

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