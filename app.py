from flask import Flask, jsonify, request
from extensions import db, migrate, bcrypt, jwt, socketio
from routes.auth import auth_bp
from routes.templates import templates_bp
from routes.inspections import inspections_bp
from routes.admins import admins_bp
from routes.organizations import organizations_bp
from routes.vehicles import vehicles_bp
from dotenv import load_dotenv
from sockets import org_events
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Load configuration from environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(templates_bp, url_prefix="/templates")
    app.register_blueprint(inspections_bp, url_prefix="/inspections")
    app.register_blueprint(organizations_bp, url_prefix="/organizations")
    app.register_blueprint(admins_bp, url_prefix="/admins")
    app.register_blueprint(vehicles_bp, url_prefix="/vehicles")
    
    
    @app.get('/')
    def index():
        return jsonify({"message": "Welcome to the Pre-Inspection API!"})


    return app
# app = create_app()
if __name__ == "__main__":
    app = create_app()
    socketio.run(app, host="0.0.0.0", port=5000)