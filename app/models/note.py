"""
Models for personal and team notes.
"""
from datetime import datetime
from app.extensions import db


class PersonalNote(db.Model):
    """Personal notes associated with a specific user"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    color = db.Column(db.String(20), default='yellow')  # Note color for UI display

    def __repr__(self):
        return f'<PersonalNote {self.title} for User {self.user_id}>'


class TeamNote(db.Model):
    """Team notes shared with all members of a team"""
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    color = db.Column(db.String(20), default='blue')  # Note color for UI display

    # Relationship to user who created the note
    user = db.relationship('User')

    def __repr__(self):
        return f'<TeamNote {self.title} for Team {self.team_id}>'