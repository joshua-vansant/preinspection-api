from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.inspection_results import InspectionResult
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

    if not driver_id or not template_id or not results:
        return jsonify({"error": "driver_id, template_id, and results are required"}), 400


    inspection_record = InspectionResult(
        driver_id=driver_id,
        template_id=template_id,
        results=results,
        created_at=db.func.now()
    )

    db.session.add(inspection_record)
    db.session.commit()

    return jsonify({
        "id": inspection_record.id,
        "driver_id": inspection_record.driver_id,
        "template_id": inspection_record.template_id,
        "results": inspection_record.results,
        "created_at": inspection_record.created_at
    }), 201

@inspections_bp.get('/history/driver/<id>')
@jwt_required()
def get_inspection_history(id):
    driver_id = get_jwt_identity()
    inspections = InspectionResult.query.filter_by(driver_id=id).all()

    return jsonify([{
        "id": inspection.id,
        "driver_id": inspection.driver_id,
        "template_id": inspection.template_id,
        "results": inspection.results,
        "created_at": inspection.created_at.isoformat()
    } for inspection in inspections]), 200