from app import create_app, db
from app.models import Room, Message, Member

def check_db():
    app = create_app('development')
    with app.app_context():
        print("Checking database tables...")
        print(f"Rooms table exists: {Room.query.count() >= 0}")
        print(f"Messages table exists: {Message.query.count() >= 0}")
        print(f"Members table exists: {Member.query.count() >= 0}")

if __name__ == "__main__":
    check_db()
