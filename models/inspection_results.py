from extensions import db
from datetime import datetime, timezone
from sqlalchemy.sql import func

class InspectionResult(db.Model):
    __tablename__ = 'inspection_results'
    __table_args__ = {"schema": "inspection_app"}

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('inspection_app.user.id'), nullable=False)
    driver = db.relationship("User", backref="inspections", lazy="joined")
    vehicle_id = db.Column(db.Integer, db.ForeignKey('inspection_app.vehicles.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('inspection_app.templates.id'), nullable=False)
    template = db.relationship("Template", backref="inspection_results", lazy="joined")
    type = db.Column(db.String(50), nullable=False)  # "pre-trip", "post-trip"
    results = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=True)  # pass, fail, needs_repair
    start_mileage = db.Column(db.Integer, nullable=True)
    end_mileage = db.Column(db.Integer, nullable=True)
    odometer_verified = db.Column(db.Boolean, default=False)
    fuel_level = db.Column(db.Float, nullable=True)  # store as percentage 0-100
    fuel_notes = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(255), nullable=True)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    @property
    def mileage(self):
        if self.type == "pre-trip":
            return self.start_mileage
        elif self.type == "post-trip":
            return self.end_mileage
        return None

    @staticmethod
    def last_for_vehicle(vehicle_id):
        return InspectionResult.query.filter_by(vehicle_id=vehicle_id).order_by(InspectionResult.created_at.desc()).first()

    def is_mileage_continuous(self):
        if self.type != "post-trip":
            return True

        last_pre = (
            InspectionResult.query
            .filter_by(vehicle_id=self.vehicle_id, type="pre-trip")
            .order_by(InspectionResult.created_at.desc())
            .first()
        )

        if not last_pre:
            return True

        return self.end_mileage == last_pre.start_mileage

    def fuel_used_since_last(self):
        last_inspection = InspectionResult.query.filter_by(vehicle_id=self.vehicle_id).order_by(InspectionResult.created_at.desc()).first()
        if not last_inspection or self.fuel_level is None or last_inspection.fuel_level is None:
            return None
        return last_inspection.fuel_level - self.fuel_level

    def to_dict(self):
        return {
            "id": self.id,
            "driver_id": self.driver_id,
            "vehicle_id": self.vehicle_id,
            "template_id": self.template_id,
            "type": self.type,
            "results": self.results,
            "status": self.status,
            "notes": self.notes,
            "start_mileage": self.start_mileage,
            "end_mileage": self.end_mileage,
            "odometer_verified": self.odometer_verified,
            "mileage": self.mileage,
            "fuel_level": self.fuel_level,
            "fuel_notes": self.fuel_notes,
            "location": self.location,
            "completed_at": self.completed_at.isoformat() + "Z" if self.completed_at else None,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None,
            "updated_at": self.updated_at.isoformat() + "Z" if self.updated_at else None
        }
