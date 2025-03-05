"""
Forms package initialization.
Import all forms here to make them available when importing the forms package.
"""
from app.forms.auth import LoginForm, UserSettingsForm
from app.forms.project import ProjectForm, ProjectStatusForm, ProjectLogForm, ProjectDocumentForm
from app.forms.milestone import MilestoneForm
from app.forms.checkpoint import CheckpointForm
from app.forms.task import TaskForm, CommentForm
from app.forms.problem import ProblemForm, ProblemCommentForm
from app.forms.note import PersonalNoteForm, TeamNoteForm, TeamForm
from app.forms.search import SearchForm

# This ensures all forms are imported and available