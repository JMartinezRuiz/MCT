"""
Milestone model representing a project phase.
"""
from datetime import datetime
from app.extensions import db


class Milestone(db.Model):
    """
    Milestone model representing a major phase or deliverable within a project
    Milestones contain checkpoints, which contain tasks
    """
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Short description
    description = db.Column(db.Text)
    sequence = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    checkpoints = db.relationship('Checkpoint', backref='milestone', cascade="all, delete-orphan", lazy=True)
    problems = db.relationship('Problem', backref='milestone', lazy=True,
                               primaryjoin="and_(Problem.milestone_id==Milestone.id, Problem.checkpoint_id==None)")

    @property
    def code(self):
        """Return the milestone code as P#-M#"""
        return f"{self.project.code}-M{self.sequence}"

    def __repr__(self):
        return f'<Milestone {self.code}: {self.name}>'