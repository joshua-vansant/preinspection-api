from extensions import db
from datetime import datetime
from sqlalchemy.sql import func

class InspectionResult(db.Model):
    __tablename__ = 'inspection_results'
    __table_args__ = {"schema": "inspection_app"}

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('inspection_app.user.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('inspection_app.vehicles.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('inspection_app.templates.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # "pre-trip", "post-trip"
    results = db.Column(db.JSON, nullable=False) 
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    notes = db.Column(db.Text, nullable=True)

    @staticmethod
    def last_for_vehicle(vehicle_id):
        return InspectionResult.query.filter_by(vehicle_id=vehicle_id).order_by(InspectionResult.created_at.desc()).first()


    # def to_dict(self):
    #     return {
    #         'id': self.id,
    #         'user_id': self.user_id,
    #         'template_id': self.template_id,
    #         'results': self.results,
    #         'created_at': self.created_at
    #     }