"""
Problem model for issue tracking.
"""
from datetime import datetime
from app.extensions import db


class Problem(db.Model):
    """
    Problem model representing issues or blockers that can occur at different levels:
    project, milestone, or checkpoint level
    """
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    milestone_id = db.Column(db.Integer, db.ForeignKey('milestone.id'), nullable=True)
    checkpoint_id = db.Column(db.Integer, db.ForeignKey('checkpoint.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(2), default='P3')  # P1 (highest) to P5 (lowest)
    status = db.Column(db.String(20), default='Open')  # Open, In progress, Resolved, Closed
    category = db.Column(db.String(50))
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    cost = db.Column(db.Float, default=0.0)
    opened_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sequence = db.Column(db.Integer, nullable=False)

    # Relationships
    comments = db.relationship('ProblemComment', backref='problem', cascade="all, delete-orphan", lazy=True)

    @property
    def code(self):
        """Return the problem code based on its location"""
        from app.models.checkpoint import Checkpoint
        from app.models.milestone import Milestone
        from app.models.project import Project

        if self.checkpoint_id:
            return f"{Checkpoint.query.get(self.checkpoint_id).code}-PB{self.sequence}"
        elif self.milestone_id:
            return f"{Milestone.query.get(self.milestone_id).code}-PB{self.sequence}"
        else:
            return f"{Project.query.get(self.project_id).code}-PB{self.sequence}"

    @property
    def full_code(self):
        """Return the full problem code including project information"""
        from app.models.checkpoint import Checkpoint
        from app.models.milestone import Milestone
        from app.models.project import Project

        project_code = Project.query.get(self.project_id).code
        if self.checkpoint_id:
            checkpoint = Checkpoint.query.get(self.checkpoint_id)
            return f"{project_code}-{checkpoint.milestone.code}-{checkpoint.code}-PB{self.sequence}"
        elif self.milestone_id:
            milestone = Milestone.query.get(self.milestone_id)
            return f"{project_code}-{milestone.code}-PB{self.sequence}"
        else:
            return f"{project_code}-PB{self.sequence}"

    def __repr__(self):
        return f'<Problem {self.code}: {self.name}>'


class ProblemComment(db.Model):
    """Comments on problems"""
    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_system = db.Column(db.Boolean, default=False)

    # Relationship
    user = db.relationship('User', foreign_keys=[user_id])

    def __repr__(self):
        return f'<ProblemComment {self.id} for Problem {self.problem_id}>'