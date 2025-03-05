"""
Models package initialization.
Import all models here to make them available when importing the models package.
"""
from app.models.user import User, user_teams
from app.models.team import Team
from app.models.project import Project, ProjectLog, ProjectDocument
from app.models.milestone import Milestone
from app.models.checkpoint import Checkpoint, CheckpointLog
from app.models.task import Task, Comment, task_in_conditions
from app.models.problem import Problem, ProblemComment
from app.models.note import PersonalNote, TeamNote

# This ensures all models are imported and recognized by SQLAlchemy