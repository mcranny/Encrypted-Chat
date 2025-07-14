from . import db
from datetime import datetime
import bcrypt
from sqlalchemy.ext.hybrid import hybrid_property

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    _password = db.Column('password', db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='room', lazy='dynamic')
    members = db.relationship('Member', backref='room', lazy='dynamic')

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext):
        self._password = bcrypt.hashpw(plaintext.encode('utf-8'), 
                                     bcrypt.gensalt()).decode('utf-8')

    def check_password(self, plaintext):
        return bcrypt.checkpw(plaintext.encode('utf-8'), 
                            self._password.encode('utf-8'))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
