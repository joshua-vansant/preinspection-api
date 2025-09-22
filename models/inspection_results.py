from extensions import db
from datetime import datetime

class InspectionResult(db.Model):
    __tablename__ = 'inspection_results'
    __table_args__ = {"schema": "inspection_app"}

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('inspection_app.user.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('inspection_app.templates.id'), nullable=False)
    results = db.Column(db.JSON, nullable=False)  # Store inspection results as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    # def to_dict(self):
    #     return {
    #         'id': self.id,
    #         'user_id': self.user_id,
    #         'template_id': self.template_id,
    #         'results': self.results,
    #         'created_at': self.created_at
    #     }