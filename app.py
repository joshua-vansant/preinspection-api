from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import User

@app.get('/')
def home():
    return 'Hello, Worlds!'

@app.get('/users')
def get_users():
    users = User.query.all()
    return {'users': [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]}

@app.post('/users')
def create_user():
    from flask import request
    data = request.get_json()
    user = User(username=data['username'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return {'message': 'User created successfully', 'user_id': user.id}