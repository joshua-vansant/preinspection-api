from flask_socketio import join_room, emit
from extensions import socketio

@socketio.on("join_org", namespace="/admin")
def handle_join_org(data):
    org_id = data.get("org_id")
    join_room(f"org_{org_id}")
    print(f"[SocketIO] Client joined org {org_id} on /admin")

def notify_driver_joined(org_id, driver_data):
    driver_data = {
        "id": driver_data.id,
        "email": driver_data.email,
        "first_name": driver_data.first_name,
        "last_name": driver_data.last_name,
        "phone_number": driver_data.phone_number,
        "role": driver_data.role,
        "org_id": driver_data.org_id,
        "created_at": driver_data.created_at.isoformat(),
        "updated_at": driver_data.updated_at.isoformat()
    }
    socketio.emit("driver_joined", driver_data, room=f"org_{org_id}")


def notify_driver_left(org_id, driver):
    data = {
        "id": driver.id,
        "email": driver.email,
        "first_name": driver.first_name,
        "last_name": driver.last_name,
        "phone_number": driver.phone_number,
        "role": driver.role,
        "org_id": driver.org_id,
        "created_at": driver.created_at.isoformat(),
        "updated_at": driver.updated_at.isoformat()
    }
    socketio.emit("driver_left", data, room=f"org_{org_id}")