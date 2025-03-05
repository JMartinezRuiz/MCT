"""
Project-related utility functions.
"""
from flask_login import current_user
from sqlalchemy import and_, or_, func

from app.extensions import db
from app.models.milestone import Milestone
from app.models.checkpoint import Checkpoint
from app.models.problem import Problem
from app.models.team import Team


def compute_milestone_status(milestone):
    """
    Compute status of a milestone based on its tasks.

    Args:
        milestone: The milestone object

    Returns:
        str: Status string ('Completed', 'In progress', or 'Pending')
    """
    total = 0
    closed = 0
    for cp in milestone.checkpoints:
        for t in cp.tasks:
            total += 1
            if t.status == 'Closed':
                closed += 1
    if total == 0:
        return 'Pending'
    return 'Completed' if closed == total else 'In progress'


def get_problem_count(project_id=None, milestone_id=None, checkpoint_id=None):
    """
    Get count of open problems for different levels.

    Args:
        project_id: Optional project ID to filter by
        milestone_id: Optional milestone ID to filter by
        checkpoint_id: Optional checkpoint ID to filter by

    Returns:
        int: Number of open problems at the specified level
    """
    query = Problem.query.filter(Problem.status.in_(['Open', 'In progress']))

    if checkpoint_id:
        return query.filter_by(checkpoint_id=checkpoint_id).count()
    elif milestone_id:
        # Include checkpoint problems
        checkpoint_problems = query.join(Checkpoint).filter(
            Checkpoint.milestone_id == milestone_id
        ).count()
        milestone_problems = query.filter_by(milestone_id=milestone_id, checkpoint_id=None).count()
        return checkpoint_problems + milestone_problems
    elif project_id:
        # Include milestone and checkpoint problems
        checkpoint_problems = query.join(Checkpoint).join(Milestone).filter(
            Milestone.project_id == project_id
        ).count()
        milestone_problems = query.join(Milestone, and_(
            Problem.milestone_id == Milestone.id,
            Problem.checkpoint_id == None
        )).filter(Milestone.project_id == project_id).count()
        project_problems = query.filter_by(project_id=project_id, milestone_id=None, checkpoint_id=None).count()
        return checkpoint_problems + milestone_problems + project_problems
    else:
        return query.count()


def update_project_cost(project_id):
    """
    Update total cost of a project based on tasks and problems.

    Args:
        project_id: ID of the project to update

    Returns:
        float: Updated total cost
    """
    from app.models.task import Task
    from app.models.project import Project

    # Calculate total task cost
    task_cost = db.session.query(func.sum(Task.cost)).join(Checkpoint).join(Milestone).filter(
        Milestone.project_id == project_id).scalar() or 0

    # Calculate total problem cost
    problem_cost = db.session.query(func.sum(Problem.cost)).filter(
        Problem.project_id == project_id).scalar() or 0

    # Update project total cost
    project = Project.query.get(project_id)
    project.total_cost = task_cost + problem_cost
    db.session.commit()

    return project.total_cost


def get_user_projects():
    """
    Get projects assigned to the current user.

    Returns:
        list: Projects assigned to current user
    """
    from app.models.project import Project

    if current_user.is_authenticated:
        # For now, return all projects
        # This could be enhanced with actual user-project relationships
        return Project.query.all()
    return []


def get_user_teams():
    """
    Get teams the current user belongs to.
    Creates default team if it doesn't exist.

    Returns:
        list: Teams the current user belongs to
    """
    if current_user.is_authenticated:
        # Check for default team and create if not exists
        default_team = Team.query.filter_by(name="Default Team").first()
        if not default_team:
            default_team = Team(name="Default Team", description="Default team for all users")
            db.session.add(default_team)
            db.session.commit()

        # Make sure user is in default team
        if default_team not in current_user.teams:
            current_user.teams.append(default_team)
            db.session.commit()

        return current_user.teams
    return []


def allowed_file(filename):
    """
    Check if a filename has an allowed extension.

    Args:
        filename: Name of the file to check

    Returns:
        bool: True if file has allowed extension, False otherwise
    """
    from flask import current_app

    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']