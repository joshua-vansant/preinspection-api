from app import app, db
from models import User

def init_database():
    with app.app_context():
        db.create_all()

        if not User.query.first():
            sample_user = User(username='admin', email='admin@example.com')
            db.session.add(sample_user)
            db.session.commit()
            print('Database initialized with sample data')
        else:
            print('Database already contains data')

if __name__ == '__main__':
    init_database()