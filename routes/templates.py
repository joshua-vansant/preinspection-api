from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.template import Template
from models.template_item import TemplateItem
from models.user import User

templates_bp = Blueprint("templates", __name__)

@templates_bp.get('/')
@jwt_required()
def get_templates():
    #Get current user
    # current_user_id = jwt.get_jwt_identity()
    current_user_id = get_jwt_identity()  
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    #Always fetch the default template
    templates = Template.query.filter(Template.is_default == True).all()

    #If user is in an org, get org templates
    # if user.org_id:
    #     org_templates = Template.query.filter(Template.created_by == user.org_id).all()
    #     templates.extend(org_templates)

    #Serialize templates
    templates_data = []
    for template in templates:
        items = TemplateItem.query.filter_by(template_id=template.id).all()
        templates_data.append({
            "id": template.id,
            "name": template.name,
            "created_by": template.created_by,
            "created_at": template.created_at,
            "is_default": template.is_default,
            "items": [{"id": item.id, "name": item.name, "question": item.question} for item in items]
        })

    return jsonify(templates_data), 200
