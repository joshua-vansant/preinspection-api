from .user import User
from .vehicle import Vehicle
from .inspection_results import InspectionResult
from .organization import Organization
from .template import Template
from .template_item import TemplateItem
from .password_reset_token import PasswordResetToken
from extensions import db

User.password_reset_tokens = db.relationship(
    'PasswordResetToken',
    backref='user',
    cascade='all, delete-orphan',
    lazy=True
)