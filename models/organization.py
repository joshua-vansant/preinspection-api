from extensions import db
from datetime import datetime
import uuid

class Organization(db.Model):
    __tablename__ = 'organizations'
    __table_args__ = {"schema": "inspection_app"}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('inspection_app.user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    invite_code = db.Column(db.String(50), unique=True, nullable=False, default=lambda: str(uuid.uuid4())[:8])
    admin_invite_code = db.Column(db.String(32), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    contact_name = db.Column(db.String(100), nullable=True)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    vehicles = db.relationship("Vehicle", backref="organization", lazy="dynamic")
    templates = db.relationship("Template", backref="organization", lazy="dynamic")


    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "admin_id": self.admin_id,
            "address": self.address,
            "phone_number": self.phone_number,
            "contact_name": self.contact_name,
            "invite_code": self.invite_code,
            "admin_invite_code": self.admin_invite_code,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

