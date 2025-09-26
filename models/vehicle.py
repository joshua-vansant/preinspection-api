from extensions import db

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    __table_args__ = {"schema": "inspection_app"}

    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey('inspection_app.organizations.id'), nullable=True)
    number = db.Column(db.String(50), nullable=True)
    make = db.Column(db.String(20), nullable=True)
    model = db.Column(db.String(20), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    vin = db.Column(db.String(25), nullable=True)
    license_plate = db.Column(db.String(10), nullable=False)
    mileage = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "org_id": self.org_id,
            "number": self.number,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "vin": self.vin,
            "license_plate": self.license_plate,
            "mileage": self.mileage,
            "status": self.status
        }

