from extensions import db
from datetime import datetime

class Template(db.Model):
    __tablename__ = 'templates'
    __table_args__ = {"schema": "inspection_app"}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('inspection_app.user.id'), nullable=False)
    items = db.relationship('TemplateItem', backref='template', cascade="all, delete-orphan")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_default = db.Column(db.Boolean, default=False)

    # def to_dict(self):
    #     return {
    #         "id": self.id,
    #         "name": self.name,
    #         "description": self.description
    #     }