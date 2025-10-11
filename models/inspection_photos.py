from extensions import db
from datetime import datetime, timezone

class InspectionPhoto(db.Model):
    __tablename__ = "inspection_photos"
    __table_args__ = {"schema": "inspection_app"}

    id = db.Column(db.Integer, primary_key=True)

    # Link to inspection (still required)
    inspection_id = db.Column(
        db.Integer,
        db.ForeignKey('inspection_app.inspection_results.id', ondelete="CASCADE"),
        nullable=False,
    )
    inspection = db.relationship("InspectionResult", backref="photos", lazy="joined")

    # Optional link to specific inspection item
    inspection_item_id = db.Column(
        db.Integer,
        db.ForeignKey('inspection_app.template_items.id', ondelete="CASCADE"),
        nullable=True,
    )
    inspection_item = db.relationship("TemplateItem", backref="photos", lazy="joined")

    # Driver who uploaded the photo
    driver_id = db.Column(
        db.Integer,
        db.ForeignKey('inspection_app.user.id', ondelete="SET NULL"),
        nullable=True,
    )
    driver = db.relationship("User", backref="uploaded_photos", lazy="joined")

    # Storage URL and timestamps
    url = db.Column('photo_url', db.String(255), nullable=False)
    uploaded_at = db.Column('created_at', db.DateTime(timezone=True), default=datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "inspection_id": self.inspection_id,
            "inspection_item_id": self.inspection_item_id,
            "driver_id": self.driver_id,
            "driver": {
                "id": self.driver.id,
                "first_name": self.driver.first_name,
                "last_name": self.driver.last_name,
            } if self.driver else None,
            "url": self.url,
            "uploaded_at": self.uploaded_at.isoformat() + "Z" if self.uploaded_at else None,
        }
