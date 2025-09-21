from extensions import db
from datetime import datetime
import uuid

class Organization(db.Model):
    __tablename__ = 'organizations'
    __table_args__ = {"schema": "inspection_app"}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('inspection_app.user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    invite_code = db.Column(db.String(50), unique=True, nullable=False, default=lambda: str(uuid.uuid4())[:8])

    # def to_dict(self):
    #     return {
    #         'id': self.id,
    #         'name': self.name,
    #         'address': self.address,
    #         'created_at': self.created_at,
    #         'updated_at': self.updated_at
    #     }