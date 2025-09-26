from extensions import db
from datetime import datetime

class TemplateItem(db.Model):
    __tablename__ = 'template_items'
    __table_args__ = {"schema": "inspection_app"}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    question = db.Column(db.String(255), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('inspection_app.templates.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    required = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "question": self.question,
            "description": self.description,
            "required": self.required,
            "order": self.order,
            "template_id": self.template_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
