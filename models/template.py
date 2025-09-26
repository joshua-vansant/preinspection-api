from extensions import db
from datetime import datetime

class Template(db.Model):
    __tablename__ = 'templates'
    __table_args__ = {"schema": "inspection_app"}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('inspection_app.user.id'), nullable=False)
    org_id = db.Column(db.Integer, db.ForeignKey('inspection_app.organizations.id'), nullable=True)
    items = db.relationship('TemplateItem', backref='template', cascade="all, delete-orphan")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_default = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, nullable=True)
    version = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by,
            "org_id": self.org_id,
            "items": [item.to_dict() for item in self.items],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_default": self.is_default,
            "version": self.version,
            "is_active": self.is_active
        }
