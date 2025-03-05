"""
Checkpoint model for project milestone checkpoints.
"""
from datetime import datetime
from app.extensions import db


class Checkpoint(db.Model):
    """
    Checkpoint model representing a specific deliverable or point of verification
    within a milestone. Checkpoints contain tasks.
    """
    id = db.Column(db.Integer, primary_key=True)
    milestone_id = db.Column(db.Integer, db.ForeignKey('milestone.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Short description
    description = db.Column(db.Text)
    sequence = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    tasks = db.relationship('Task', backref='checkpoint', cascade="all, delete-orphan", lazy=True)
    problems = db.relationship('Problem', backref='checkpoint', lazy=True)
    logs = db.relationship('CheckpointLog', backref='checkpoint', cascade="all, delete-orphan", lazy=True)

    @property
    def code(self):
        """Return the checkpoint code as P#-M#-C#"""
        return f"{self.milestone.code}-C{self.sequence}"

    def __repr__(self):
        return f'<Checkpoint {self.code}: {self.name}>'


class CheckpointLog(db.Model):
    """Log entries for tracking checkpoint activity"""
    id = db.Column(db.Integer, primary_key=True)
    checkpoint_id = db.Column(db.Integer, db.ForeignKey('checkpoint.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_system = db.Column(db.Boolean, default=False)

    # Relationship
    user = db.relationship('User', foreign_keys=[user_id])

    def __repr__(self):
        return f'<CheckpointLog {self.id} for Checkpoint {self.checkpoint_id}>'