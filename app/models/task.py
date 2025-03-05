"""
Task model for project work items.
"""
from datetime import datetime
from app.extensions import db

# Association table for task dependencies
task_in_conditions = db.Table('task_in_conditions',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('required_task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True)
)

class Task(db.Model):
    """
    Task model representing a specific work item within a checkpoint
    Tasks can depend on other tasks through in_conditions relationship
    """
    id = db.Column(db.Integer, primary_key=True)
    checkpoint_id = db.Column(db.Integer, db.ForeignKey('checkpoint.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Short description
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')  # Pending, Open, In progress, Closed, On hold
    sequence = db.Column(db.Integer, nullable=False)
    size = db.Column(db.String(2), default='S5')
    category = db.Column(db.String(50))
    subcategory = db.Column(db.String(50))
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    cost = db.Column(db.Float, default=0.0)
    opened_at = db.Column(db.DateTime, nullable=True)
    work_time = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    comments = db.relationship('Comment', backref='task', cascade="all, delete-orphan", lazy=True)
    in_conditions = db.relationship('Task', secondary=task_in_conditions,
                                  primaryjoin=(id == task_in_conditions.c.task_id),
                                  secondaryjoin=(id == task_in_conditions.c.required_task_id),
                                  backref='dependent_tasks')

    @property
    def code(self):
        """Return the task code as P#-M#-C#-T#"""
        return f"{self.checkpoint.code}-T{self.sequence}"

    @property
    def full_code(self):
        """Return the full task code"""
        return f"{self.checkpoint.milestone.project.code}-{self.checkpoint.milestone.code}-{self.checkpoint.code}-T{self.sequence}"

    @property
    def out_condition(self):
        """Return the output condition code for this task"""
        return f"{self.code}-closed"

    def __repr__(self):
        return f'<Task {self.code}: {self.name}>'


class Comment(db.Model):
    """Comments on tasks"""
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_system = db.Column(db.Boolean, default=False)

    # Relationship
    user = db.relationship('User', foreign_keys=[user_id])

    def __repr__(self):
        return f'<Comment {self.id} for Task {self.task_id}>'