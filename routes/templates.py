from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.template import Template
from models.template_item import TemplateItem
from models.user import User
from extensions import db
from sqlalchemy import or_

templates_bp = Blueprint("templates", __name__)

@templates_bp.get('/')
@jwt_required()
def get_templates():
    current_user_id = get_jwt_identity()  
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    templates = (
        Template.query
        .filter(
            or_(
                Template.is_default == True,
                Template.org_id == user.org_id
            )
        )
        .distinct()
        .all()
    )

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
            "items": [
                {"id": item.id, "name": item.name, "question": item.question}
                for item in items
            ]
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
    name = data.get("name")
    items_data = data.get("items", [])
    is_default = data.get("is_default", False)

    if not name:
        return jsonify({"error": "Name is required"}), 400

    for item in items_data:
        if not item.get("name") or not item.get("question"):
            return jsonify({"error": "Each item requires a name and question"}), 400

    new_template = Template(
        name=name,
        created_by=current_user_id,
        org_id=user.org_id,
        created_at=db.func.now(),
        is_default=is_default
    )
    db.session.add(new_template)
    db.session.flush()  # to get new_template.id

    for item in items_data:
        new_item = TemplateItem(
            name=item["name"],
            question=item["question"],
            template_id=new_template.id
        )
        db.session.add(new_item)

    db.session.commit()

    return jsonify({"message": "Template created successfully", "id": new_template.id}), 201


@templates_bp.put('/<int:template_id>/edit')
@jwt_required()
def edit_template(template_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    claims = get_jwt()
    role = claims.get("role")
    if role != "admin":
        return jsonify({"error": "Only admins can edit templates"}), 403

    data = request.get_json()
    name = data.get("name")
    items_data = data.get("items", [])
    is_default = data.get("is_default", False)

    template = Template.query.get(template_id)
    if not template or template.org_id != user.org_id:
        return jsonify({"error": "Template not found"}), 404

    if not name:
        return jsonify({"error": "Name is required"}), 400

    # Update template fields
    template.name = name
    template.is_default = is_default

    # Clear old items and add new
    TemplateItem.query.filter_by(template_id=template.id).delete()
    for item in items_data:
        if not item.get("name") or not item.get("question"):
            return jsonify({"error": "Each item requires a name and question"}), 400
        new_item = TemplateItem(
            name=item["name"],
            question=item["question"],
            template_id=template.id,
        )
        db.session.add(new_item)

    db.session.commit()

    return jsonify({"message": "Template updated successfully"}), 200
