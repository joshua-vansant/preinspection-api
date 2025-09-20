from extensions import db
from datetime import datetime

class TemplateItem(db.Model):
    __tablename__ = 'template_items'
    __table_args__ = {"schema": "inspection_app"}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    question = db.Column(db.String(255), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('inspection_app.templates.id'), nullable=False)

    # def to_dict(self):
    #     return {
    #         'id': self.id,
    #         'name': self.name,
    #         'description': self.description,
    #         'created_at': self.created_at,
    #         'updated_at': self.updated_at
    #     }