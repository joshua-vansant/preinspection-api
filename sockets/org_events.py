from flask_socketio import join_room, emit
from extensions import socketio

@socketio.on("join_org")
def handle_join_org(data):
    org_id = data.get("org_id")
    join_room(f"org_{org_id}")
    print(f"Client joined org {org_id}")

def notify_driver_joined(org_id, driver_data):
    driver_data = {
        "id": driver_data.id,
        "email": driver_data.email
    }
    socketio.emit("driver_joined", driver_data, room=f"org_{org_id}")

def notify_driver_left(org_id, driver):
    data = {
        "id": driver.id,
        "email": driver.email
    }
    socketio.emit("driver_left", data, room=f"org_{org_id}")
