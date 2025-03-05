"""
User model for authentication and user-related data.
"""
from app.extensions import db
from flask_login import UserMixin
from datetime import datetime

# Association table for user-team many-to-many relationship
user_teams = db.Table('user_teams',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                      db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True)
                      )


class User(db.Model, UserMixin):
    """User model for authentication and profile data"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    first_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    profile_image = db.Column(db.String(120), nullable=True, default='avatar1.png')

    # Define relationships
    tasks = db.relationship('Task', backref='assigned_to', lazy=True)
    problems = db.relationship('Problem', backref='assigned_to', lazy=True)
    teams = db.relationship('Team', secondary=user_teams, backref=db.backref('members', lazy='dynamic'))
    personal_notes = db.relationship('PersonalNote', backref='user', lazy=True, cascade="all, delete-orphan")

    @property
    def full_name(self):
        """Return the user's full name or username if no name is set"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        return self.username