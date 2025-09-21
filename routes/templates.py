from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.template import Template
from models.template_item import TemplateItem
from models.user import User
from extensions import db

templates_bp = Blueprint("templates", __name__)

@templates_bp.get('/')
@jwt_required()
def get_templates():
    current_user_id = get_jwt_identity()  
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    #Always fetch the default template
    templates = Template.query.filter(Template.is_default == True).all()

    #If user is in an org, get org templates
    if user.org_id:
        org_templates = Template.query.filter(Template.created_by == user.org_id).all()
        templates.extend(org_templates)

    templates_data = []
    for template in templates:
        items = TemplateItem.query.filter_by(template_id=template.id).all()
        templates_data.append({
            "id": template.id,
            "name": template.name,
            "created_by": template.created_by,
            "org_id": template.org_id,
            "created_at": template.created_at,
            "is_default": template.is_default,
            "items": [{"id": item.id, "name": item.name, "question": item.question} for item in items]
        })

    return jsonify(templates_data), 200


@templates_bp.post('/create')
@jwt_required()
def create_template():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    claims = get_jwt()
    role = claims.get("role")
    if role != "admin":
        return jsonify({"error": "Only admins can create templates"}), 403

    data = request.get_json()
    name = data.get('name')
    created_by = current_user_id
    org_id = user.org_id if 'org_id' in data else None
    items_data = data.get('items', [])
    created_at = data.get('created_at')
    is_default = data.get('is_default', False)

    if not name:
        return jsonify({"error": "Name is required"}), 400

    new_template = Template(name=name, created_by=created_by, org_id=org_id, created_at=created_at, is_default=is_default)
    db.session.add(new_template)
    db.session.flush()  # Flush to get the new template ID

    # Create TemplateItem records
    for item in items_data:
        new_item = TemplateItem(
            name=item.get("name"),
            question=item.get("question"),
            template_id=new_template.id
        )
        db.session.add(new_item)

    db.session.commit()

    return jsonify({"message": "Template created successfully", "id": new_template.id}), 201