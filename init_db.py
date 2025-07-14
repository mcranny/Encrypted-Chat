from app import create_app, db
from app.models import Room, Message, Member

def init_db():
    app = create_app('development')
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
