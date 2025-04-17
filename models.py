# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Faculty(UserMixin, db.Model):
    """Faculty model for storing faculty details and login information."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64), nullable=False)
    department = db.Column(db.String(64))
    courses = db.relationship('Course', backref='instructor', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Faculty {self.name}>'

class Division(db.Model):
    """Division model for storing student divisions."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    courses = db.relationship('Course', backref='division', lazy='dynamic')
    
    def __repr__(self):
        return f'<Division {self.name}>'

class Room(db.Model):
    """Room model for classrooms and labs."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    capacity = db.Column(db.Integer, default=30)
    is_lab = db.Column(db.Boolean, default=False)
    courses = db.relationship('Course', backref='room', lazy='dynamic')
    
    def __repr__(self):
        return f'<Room {self.name}>'

class TimeSlot(db.Model):
    """TimeSlot model for defining available time slots."""
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    courses = db.relationship('Course', backref='time_slot', lazy='dynamic')
    
    def __repr__(self):
        return f'<TimeSlot {self.day} {self.start_time}-{self.end_time}>'

class Course(db.Model):
    """Course model for storing course details and scheduling information."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    division_id = db.Column(db.Integer, db.ForeignKey('division.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    time_slot_id = db.Column(db.Integer, db.ForeignKey('time_slot.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Course {self.name}>'
