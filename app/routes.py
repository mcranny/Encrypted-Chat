from flask import Blueprint, render_template, request, session
from flask_socketio import emit, join_room, leave_room
from . import socketio, db
from .models import Room, Message, Member

main = Blueprint('main', __name__)

active_users = {}

@main.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('create_room')
def on_create_room(data):
    try:
        room_name = data.get('room')
        password = data.get('password')
        
        if not room_name or not password:
            emit('error', {'message': 'Room name and password required'})
            return

        if Room.query.filter_by(name=room_name).first():
            emit('error', {'message': 'Room already exists'})
            return

        # Create new room
        room = Room(name=room_name)
        room.password = password  # This will hash the password
        db.session.add(room)
        db.session.commit()

        join_room(room_name)
        emit('room_created', {'room': room_name})
        
    except Exception as e:
        db.session.rollback()
        emit('error', {'message': 'Failed to create room'})
        print(f"Error creating room: {str(e)}")

@socketio.on('join_room')
def on_join(data):
    try:
        room_name = data.get('room')
        password = data.get('password')
        username = data.get('username')

        room = Room.query.filter_by(name=room_name).first()
        if not room:
            emit('error', {'message': 'Room not found'})
            return

        if not room.check_password(password):
            emit('error', {'message': 'Invalid password'})
            return

        # Add member to room
        member = Member(room_id=room.id, username=username)
        db.session.add(member)
        db.session.commit()

        join_room(room_name)
        active_users[room_name] = active_users.get(room_name, set())
        active_users[room_name].add(username)

        # Get recent messages
        recent_messages = Message.query.filter_by(room_id=room.id)\
                                    .order_by(Message.timestamp.desc())\
                                    .limit(50).all()
        
        # Emit join event to the joining user with message history
        emit('user_joined', {
            'username': username,
            'room': room_name,
            'recent_messages': [
                {'username': msg.username, 'content': msg.content}
                for msg in reversed(recent_messages)
            ]
        })
        
        # Emit join notification to other users (without message history)
        emit('user_joined', {
            'username': username,
            'room': room_name
        }, room=room_name, include_self=False)

    except Exception as e:
        db.session.rollback()
        emit('error', {'message': 'Failed to join room'})
        print(f"Error joining room: {str(e)}")

@socketio.on('message')
def on_message(data):
    try:
        room_name = data.get('room')
        content = data.get('message')
        username = data.get('username')

        room = Room.query.filter_by(name=room_name).first()
        if not room:
            return

        message = Message(content=content, room_id=room.id, username=username)
        db.session.add(message)
        db.session.commit()

        emit('message', {
            'username': username,
            'message': content
        }, room=room_name)

    except Exception as e:
        db.session.rollback()
        print(f"Error sending message: {str(e)}")

@socketio.on('leave_room')
def on_leave(data):
    try:
        room_name = data.get('room')
        username = data.get('username')

        if room_name in active_users and username in active_users[room_name]:
            active_users[room_name].remove(username)

        room = Room.query.filter_by(name=room_name).first()
        if room:
            member = Member.query.filter_by(room_id=room.id, username=username).first()
            if member:
                db.session.delete(member)
                db.session.commit()

        leave_room(room_name)
        emit('user_left', {'username': username}, room=room_name)

    except Exception as e:
        db.session.rollback()
        print(f"Error leaving room: {str(e)}")

@socketio.on('disconnect')
def on_disconnect():
    print("Client disconnected")
