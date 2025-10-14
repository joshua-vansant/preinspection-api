from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from firebase_admin import storage
from werkzeug.utils import secure_filename
from models.inspection_results import InspectionResult
from models.template import Template
from models.vehicle import Vehicle
from models.user import User
from models.inspection_photos import InspectionPhoto
from extensions import db, socketio
from datetime import datetime, timezone
import uuid

inspections_bp = Blueprint("inspections", __name__)

def driver_can_access(user, inspection):
#    - Driver can always access their own inspections.
#    - Driver can access inspections with driver_id=None but org_id matching their org.
    if inspection.driver_id == user.id:
        return True
    if user.org_id and inspection.driver_id is None and inspection.org_id == user.org_id:
        return True
    return False


# Helper to filter queries by driver/org access
def filter_by_driver_access(query, user):
    if user.org_id:
        return query.filter(
            (InspectionResult.driver_id == user.id) |
            ((InspectionResult.driver_id == None) & (InspectionResult.org_id == user.org_id))
        )
    else:
        return query.filter_by(driver_id=user.id)

# --
# Submit inspection
# --
@inspections_bp.post('/submit')
@jwt_required()
def submit_inspection():
    data = request.get_json()
    driver_id = int(get_jwt_identity())
    inspection_id = data.get('inspection_id') 
    template_id = data.get('template_id')
    vehicle_id = data.get('vehicle_id')
    inspection_type = data.get('type')
    results = data.get('results')
    notes = data.get('notes')
    start_mileage = data.get("start_mileage")

    # Basic validations 
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

    # Template validation 
    template = Template.query.get(template_id)
    if not template:
        return jsonify({"error": "Template not found"}), 404
    driver = User.query.get(driver_id)
    if template.org_id is not None and driver.org_id != template.org_id:
        return jsonify({"error": "Template does not belong to your organization"}), 403

    # Vehicle / mileage validation 
    vehicle = Vehicle.query.get(vehicle_id)
    if vehicle and vehicle.mileage is not None and start_mileage < vehicle.mileage:
        return jsonify({"error": "start_mileage cannot be less than vehicle's current mileage"}), 400

    # --- Create / update inspection ---
    if inspection_id:
        inspection_record = InspectionResult.query.get(inspection_id)
        if not inspection_record:
            return jsonify({"error": "Draft inspection not found"}), 404
        # Update existing draft
        inspection_record.results = results
        inspection_record.notes = notes
        inspection_record.start_mileage = start_mileage
        inspection_record.fuel_level = data.get("fuel_level")
        inspection_record.fuel_notes = data.get("fuel_notes")
        inspection_record.odometer_verified = data.get("odometer_verified", False)
        inspection_record.is_draft = False
        # Populate driver snapshot
        inspection_record.driver_first_name = driver.first_name
        inspection_record.driver_last_name = driver.last_name
        inspection_record.driver_full_name = f"{driver.first_name} {driver.last_name}"
    else:
        # Look for existing draft
        draft = InspectionResult.query.filter_by(
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            template_id=template_id,
            is_draft=True
        ).first()
        if draft:
            draft.results = results
            draft.notes = notes
            draft.start_mileage = start_mileage
            draft.fuel_level = data.get("fuel_level")
            draft.fuel_notes = data.get("fuel_notes")
            draft.odometer_verified = data.get("odometer_verified", False)
            draft.is_draft = False
            draft.driver_first_name = driver.first_name
            draft.driver_last_name = driver.last_name
            draft.driver_full_name = f"{driver.first_name} {driver.last_name}"
            inspection_record = draft
        else:
            inspection_record = InspectionResult(
                driver_id=driver_id,
                vehicle_id=vehicle_id,
                template_id=template_id,
                type=inspection_type,
                results=results or {},
                created_at=datetime.now(timezone.utc),
                notes=notes,
                start_mileage=start_mileage,
                fuel_level=data.get("fuel_level"),
                fuel_notes=data.get("fuel_notes"),
                odometer_verified=data.get("odometer_verified", False),
                org_id=driver.org_id,
                is_draft=False,
                driver_first_name=driver.first_name,
                driver_last_name=driver.last_name,
                driver_full_name=f"{driver.first_name} {driver.last_name}"
            )
            db.session.add(inspection_record)

    # Update vehicle mileage 
    if vehicle:
        vehicle.mileage = start_mileage

    db.session.commit()

    # Cleanup leftover drafts
    db.session.query(InspectionResult).filter(
        InspectionResult.driver_id == driver_id,
        InspectionResult.vehicle_id == vehicle_id,
        InspectionResult.is_draft == True
    ).delete()
    db.session.commit()

    # Socket emit
    if driver.org_id:
        socketio.emit(
            "inspection_created",
            {
                inspection_record.to_dict(),
            },
            room=f"org_{driver.org_id}",
        )

    return jsonify(inspection_record.to_dict()), 201


# --
# Get inspection history
# --
@inspections_bp.get('/history')
@jwt_required()
def get_inspection_history():
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")
    user = User.query.get(user_id)

    if role == "driver":
        inspections_query = filter_by_driver_access(InspectionResult.query, user)
        inspections = inspections_query.all()
    elif role == "admin":
        if not user.org_id:
            return jsonify({"error": "Admin has no org"}), 400
        inspections = InspectionResult.query.filter_by(org_id=user.org_id).all()
    else:
        return jsonify({"error": "Unauthorized role"}), 403

    response = [insp.to_dict() for insp in inspections]
    return jsonify(response), 200



# --
# Get single inspection
# --
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

    response = inspection.to_dict()
    template = Template.query.get(inspection.template_id)
    if template:
        response["template"] = template.to_dict()

    return jsonify(response), 200



# --
# Get last inspection for a vehicle
# --
@inspections_bp.get('/last/<int:vehicle_id>')
@jwt_required()
def get_last_inspection(vehicle_id):
    user = User.query.get(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    query = InspectionResult.query.filter_by(vehicle_id=vehicle_id).order_by(InspectionResult.created_at.desc())
    if role == "driver":
        query = filter_by_driver_access(query, user)

    last_inspection = query.first()
    if not last_inspection:
        return jsonify({"message": "No inspections found for this vehicle"}), 200

    return jsonify(last_inspection.to_dict()), 200



# --
# Update inspection
# --
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

    # Mileage validation 
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


# --
# Start Inspection
# --
@inspections_bp.post('/start')
@jwt_required()
def start_inspection():
    driver_id = int(get_jwt_identity())
    data = request.get_json()
    vehicle_id = data.get('vehicle_id')
    template_id = data.get('template_id')

    if not vehicle_id:
        return jsonify({"error": "vehicle_id is required"}), 400

    driver = User.query.get(driver_id)
    org_id = driver.org_id

    # Check for existing draft
    query = InspectionResult.query.filter_by(
        driver_id=driver_id,
        vehicle_id=vehicle_id,
        is_draft=True
    )
    if template_id is not None:
        query = query.filter(InspectionResult.template_id == template_id)
    else:
        query = query.filter(InspectionResult.template_id.is_(None))

    existing_draft = query.first()
    if existing_draft:
        return jsonify({
            "message": "Existing draft found, resuming inspection.",
            "inspection_id": existing_draft.id
        }), 200

    # Determine inspection type based on last inspection
    last_inspection_query = InspectionResult.query.filter_by(
        driver_id=driver_id,
        vehicle_id=vehicle_id,
        is_draft=False
    )
    if org_id:
        last_inspection_query = last_inspection_query.filter_by(org_id=org_id)

    last_inspection = last_inspection_query.order_by(
        InspectionResult.created_at.desc()
    ).first()

    if not last_inspection:
        inspection_type = 'pre'
    elif last_inspection.type.lower() == 'pre':
        inspection_type = 'post'
    else:
        inspection_type = 'pre'

    # Create new draft inspection
    inspection = InspectionResult(
        driver_id=driver_id,
        vehicle_id=vehicle_id,
        type=inspection_type,
        template_id=template_id,
        created_at=datetime.now(timezone.utc),
        org_id=org_id,
        results=data.get('results') or {},
        is_draft=True,
        driver_first_name=driver.first_name,
        driver_last_name=driver.last_name,
        driver_full_name=f"{driver.first_name} {driver.last_name}"
    )

    db.session.add(inspection)
    db.session.commit()

    return jsonify({
        "message": "New draft inspection created.",
        "inspection_id": inspection.id,
        "type": inspection_type
    }), 201


# --
# Upload Photo
# --
@inspections_bp.post('/upload-photo')
@jwt_required()
def upload_inspection_photo():
    driver_id = int(get_jwt_identity())

    # Optional fields
    inspection_id = request.form.get('inspection_id', type=int)
    inspection_item_id = request.form.get('inspection_item_id', type=int)

    # Validate file
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Verify inspection exists (required)
    if not inspection_id:
        return jsonify({"error": "inspection_id is required"}), 400

    inspection = InspectionResult.query.get(inspection_id)
    if not inspection:
        return jsonify({"error": "Inspection not found"}), 404

    print("DEBUG: Received inspection_id:", inspection_id)
    print("DEBUG: Received inspection_item_id:", inspection_item_id)
    print("DEBUG: inspection.template_id:", inspection.template_id)
    # Verify item belongs to the same template (if provided)
    if inspection_item_id:
        from models.template_item import TemplateItem 
        item = TemplateItem.query.get(inspection_item_id)
        print("DEBUG: item.template_id:", getattr(item, 'template_id', None))
        if not item:
            return jsonify({"error": "Invalid inspection_item_id"}), 400
        if item.template_id != inspection.template_id:
            return jsonify({"error": "Item does not belong to inspection's template"}), 400

    # Generate unique filename
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"

    org_id = inspection.org_id or 'no-org'
    item_segment = f"items/{inspection_item_id}/" if inspection_item_id else ""
    storage_path = f"orgs/{org_id}/inspections/{inspection.id}/{item_segment}{unique_filename}"

    # Upload to Firebase
    bucket = storage.bucket()
    blob = bucket.blob(storage_path)
    blob.upload_from_file(file, content_type=file.content_type)
    photo_url = blob.public_url

    # Save to DB
    new_photo = InspectionPhoto(
        inspection_id=inspection.id,
        inspection_item_id=inspection_item_id,
        driver_id=driver_id,
        url=photo_url
    )

    print("DEBUG: Uploading file:", file.filename)
    print("DEBUG: Storage path:", storage_path)

    db.session.add(new_photo)
    db.session.commit()

    return jsonify({
        "photo_url": photo_url,
        "inspection_id": inspection.id,
        "inspection_item_id": inspection_item_id
    }), 200
