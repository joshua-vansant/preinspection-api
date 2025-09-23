from flask import Blueprint, jsonify
from extensions import db
from models.vehicle import Vehicle

vehicles_bp = Blueprint("vehicles", __name__)

@vehicles_bp.get('/')
def get_vehicles():
    vehicles = Vehicle.query.all()
    return jsonify([{
        "id": v.id,
        "org_id": v.org_id,
        "number": v.number
    } for v in vehicles]), 200
