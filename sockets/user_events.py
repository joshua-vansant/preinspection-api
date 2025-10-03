from flask_socketio import emit
from extensions import socketio

def notify_user_updated(org_id, user):
    user_data = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "role": user.role,
        "org_id": user.org_id,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
    }

    socketio.emit("user_updated", user_data, room=f"org_{org_id}")
