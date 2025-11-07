from datetime import datetime, timedelta
import uuid
from extensions import db

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    __table_args__ = {'schema': 'inspection_app'}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('inspection_app.user.id', ondelete='CASCADE'),
        nullable=False
    )
    token = db.Column(db.String(128), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @staticmethod
    def generate(user_id, lifetime_minutes=30):
        token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(minutes=lifetime_minutes)
        return PasswordResetToken(user_id=user_id, token=token, expires_at=expires_at)

    def is_expired(self):
        return datetime.utcnow() > self.expires_at
