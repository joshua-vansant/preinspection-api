from extensions import db
from datetime import datetime, timezone
from sqlalchemy.sql import func
from sqlalchemy.orm import validates


class InspectionResult(db.Model):
    __tablename__ = 'inspection_results'
    __table_args__ = {"schema": "inspection_app"}

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('inspection_app.user.id'), nullable=True)
    driver = db.relationship("User", backref="inspections", lazy="joined")
    vehicle_id = db.Column(db.Integer, db.ForeignKey('inspection_app.vehicles.id', ondelete="SET NULL"), nullable=True)
    template_id = db.Column(db.Integer, db.ForeignKey('inspection_app.templates.id'), nullable=True)
    template = db.relationship("Template", backref="inspection_results", lazy="joined")
    org_id = db.Column(db.Integer, db.ForeignKey('inspection_app.organizations.id'), nullable=True)
    type = db.Column(db.String(50), nullable=False)  # "pre-trip", "post-trip"
    results = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=True)  # pass, fail, needs_repair
    start_mileage = db.Column(db.Integer, nullable=False)
    odometer_verified = db.Column(db.Boolean, default=False)
    fuel_level = db.Column(db.Float, nullable=True)  # store as percentage 0-100
    fuel_notes = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(255), nullable=True)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    @staticmethod
    def last_for_vehicle(vehicle_id):
        return (InspectionResult.query
                .filter_by(vehicle_id=vehicle_id)
                .order_by(InspectionResult.created_at.desc())
                .first())

    def fuel_used_since_last(self):
        last_inspection = (InspectionResult.query
                           .filter_by(vehicle_id=self.vehicle_id)
                           .order_by(InspectionResult.created_at.desc())
                           .first())
        if not last_inspection or self.fuel_level is None or last_inspection.fuel_level is None:
            return None
        return last_inspection.fuel_level - self.fuel_level

    @validates("start_mileage")
    def validate_mileage(self, key, value):
        """Ensure start_mileage is always present."""
        if value is None:
            raise ValueError("All inspections must include start_mileage.")
        return value

    def to_dict(self):
        return {
            "id": self.id,
            "driver_id": self.driver_id,
            "vehicle_id": self.vehicle_id,
            "template_id": self.template_id,
            "org_id": self.org_id,
            "type": self.type,
            "results": self.results,
            "status": self.status,
            "notes": self.notes,
            "start_mileage": self.start_mileage,
            "odometer_verified": self.odometer_verified,
            "fuel_level": self.fuel_level,
            "fuel_notes": self.fuel_notes,
            "location": self.location,
            "completed_at": self.completed_at.isoformat() + "Z" if self.completed_at else None,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None,
            "updated_at": self.updated_at.isoformat() + "Z" if self.updated_at else None
        }
