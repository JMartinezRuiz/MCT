"""
Project model for project management and related functionality.
"""
from datetime import datetime
from sqlalchemy import and_, or_
from app.extensions import db


class Project(db.Model):
    """Project model representing the main organizational unit"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    subcategory = db.Column(db.String(50))
    size = db.Column(db.String(2), default='S3')
    importance = db.Column(db.String(2), default='P5')
    status = db.Column(db.String(20), default='Planning')  # Planning, Open, Review, Closed
    budget = db.Column(db.Float, default=0.0)
    total_cost = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    milestones = db.relationship('Milestone', backref='project', cascade="all, delete-orphan", lazy=True)
    problems = db.relationship('Problem', backref='project', lazy=True,
                               primaryjoin="and_(Problem.project_id==Project.id, "
                                           "Problem.milestone_id==None, Problem.checkpoint_id==None)")
    logs = db.relationship('ProjectLog', backref='project', cascade="all, delete-orphan", lazy=True)
    documents = db.relationship('ProjectDocument', backref='project', cascade="all, delete-orphan", lazy=True)

    @property
    def code(self):
        """Return the project code as P{id}"""
        return f"P{self.id}"

    def get_progress(self):
        """
        Calculate project progress percentage based on completed tasks

        Returns:
            int: Percentage of completed tasks (0-100)
        """
        total_tasks = 0
        completed_tasks = 0

        for milestone in self.milestones:
            for checkpoint in milestone.checkpoints:
                for task in checkpoint.tasks:
                    total_tasks += 1
                    if task.status == 'Closed':
                        completed_tasks += 1

        if total_tasks == 0:
            return 0

        return int((completed_tasks / total_tasks) * 100)

    def __repr__(self):
        return f'<Project {self.name}>'


class ProjectLog(db.Model):
    """Log entries for tracking project activity"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_system = db.Column(db.Boolean, default=False)

    # Relationship
    user = db.relationship('User', foreign_keys=[user_id])

    def __repr__(self):
        return f'<ProjectLog {self.id} for Project {self.project_id}>'


class ProjectDocument(db.Model):
    """Documents attached to projects"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    def __repr__(self):
        return f'<ProjectDocument {self.title}>'