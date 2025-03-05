"""
Team model for team organization and management.
"""
from datetime import datetime
from app.extensions import db


class Team(db.Model):
    """
    Team model representing groups of users that can work together
    and share team notes
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship - team notes associated with this team
    team_notes = db.relationship('TeamNote', backref='team', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Team {self.name}>'