from extensions import db

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    __table_args__ = {"schema": "inspection_app"}

    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey('inspection_app.organizations.id'), nullable=True)
    number = db.Column(db.String(50), nullable=True)

    # def to_dict(self):
    #     return {
    #         "id": self.id,
    #         "org_id": self.org_id,
    #         "number": self.number
    #     }
