"""
Main routes for dashboard and search functionality.
"""
import re
from datetime import datetime
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import or_, and_

from app.extensions import db
from app.blueprints.main import bp
from app.models.project import Project
from app.models.milestone import Milestone
from app.models.checkpoint import Checkpoint
from app.models.task import Task
from app.models.problem import Problem
from app.models.note import PersonalNote, TeamNote
from app.utils.project import get_user_teams
from flask import current_app
import os


@bp.route('/debug-path')
def debug_path():
    template_path = current_app.template_folder
    exists = os.path.exists(os.path.join(template_path, 'dashboard.html'))
    return f"Looking for templates in: {template_path}<br>dashboard.html exists: {exists}"

@bp.route('/')
@login_required
def dashboard():
    """Main dashboard view showing overview of projects and tasks"""
    projects = Project.query.all()

    # Count active tasks (not counting 'Pending')
    active_tasks = Task.query.filter(
        Task.assigned_to_id == current_user.id,
        Task.status.in_(['Open', 'In progress', 'On hold'])
    ).count()

    # Get open problems
    total_open_problems = Problem.query.filter(Problem.status.in_(['Open', 'In progress'])).count()
    current_date = datetime.utcnow().strftime("%Y-%m-%d")

    # Get recent problems
    recent_problems = Problem.query.filter(Problem.status.in_(['Open', 'In progress'])) \
        .order_by(Problem.opened_at.desc()).limit(5).all()

    # Get tasks assigned to current user
    current_user_tasks = Task.query.filter_by(assigned_to_id=current_user.id).all()

    # Get open projects for the progress chart
    open_projects = Project.query.filter_by(status='Open').all()

    # Get user's personal notes
    personal_notes = PersonalNote.query.filter_by(user_id=current_user.id).order_by(
        PersonalNote.updated_at.desc()).all()

    # Get user's team notes from all teams they belong to
    user_teams = get_user_teams()
    team_notes = []
    for team in user_teams:
        team_notes.extend(TeamNote.query.filter_by(team_id=team.id).order_by(TeamNote.updated_at.desc()).all())

    return render_template('dashboard.html',
                           projects=projects,
                           active_tasks=active_tasks,
                           total_open_problems=total_open_problems,
                           recent_problems=recent_problems,
                           current_user_tasks=current_user_tasks,
                           current_date=current_date,
                           open_projects=open_projects,
                           personal_notes=personal_notes,
                           team_notes=team_notes,
                           user_teams=user_teams)


@bp.route('/search')
@login_required
def search():
    """Global search functionality for finding tasks and problems"""
    query = request.args.get('q', '')
    results = []

    if not query:
        return render_template('search_results.html', results=results, query=query)

    # Pattern for parsing the search query
    # This will match patterns like P1-M1-C1-T1, M1-C1-*, etc.
    pattern = r'^(?:(?P<project>P\d+)-)?(?:(?P<milestone>M\d+)-)?(?:(?P<checkpoint>C\d+)-)?(?P<item>T\d+|PB\d+|\*)$'

    match = re.match(pattern, query, re.IGNORECASE)

    if match:
        groups = match.groupdict()

        project_code = groups.get('project')
        milestone_code = groups.get('milestone')
        checkpoint_code = groups.get('checkpoint')
        item_code = groups.get('item')

        # First, filter by project if provided
        project_filter = None
        if project_code:
            project_id = int(project_code[1:])
            project = Project.query.get(project_id)
            if not project:
                return render_template('search_results.html', results=[], query=query)
            project_filter = project.id

        # Filter by milestone if provided
        milestone_filter = None
        if milestone_code:
            milestone_seq = int(milestone_code[1:])
            milestones = Milestone.query.filter_by(sequence=milestone_seq)

            if project_filter:
                milestones = milestones.filter_by(project_id=project_filter)

            milestone = milestones.first()
            if not milestone:
                return render_template('search_results.html', results=[], query=query)
            milestone_filter = milestone.id

        # Filter by checkpoint if provided
        checkpoint_filter = None
        if checkpoint_code:
            checkpoint_seq = int(checkpoint_code[1:])
            checkpoints = Checkpoint.query.filter_by(sequence=checkpoint_seq)

            if milestone_filter:
                checkpoints = checkpoints.filter_by(milestone_id=milestone_filter)

            checkpoint = checkpoints.first()
            if not checkpoint:
                return render_template('search_results.html', results=[], query=query)
            checkpoint_filter = checkpoint.id

        # Now search for the specific item
        if item_code == '*':
            # Wildcard search - get all tasks and problems for the filtered checkpoint
            if checkpoint_filter:
                tasks = Task.query.filter_by(checkpoint_id=checkpoint_filter).all()
                problems = Problem.query.filter_by(checkpoint_id=checkpoint_filter).all()
                results = [(task, 'task') for task in tasks] + [(problem, 'problem') for problem in problems]
            elif milestone_filter:
                # Find all checkpoints in the milestone
                checkpoints = Checkpoint.query.filter_by(milestone_id=milestone_filter).all()
                tasks = Task.query.join(Checkpoint).filter(Checkpoint.milestone_id == milestone_filter).all()
                problems = Problem.query.filter(
                    or_(
                        Problem.milestone_id == milestone_filter,
                        and_(Problem.checkpoint_id != None,
                             Problem.checkpoint.has(Checkpoint.milestone_id == milestone_filter))
                    )
                ).all()
                results = [(task, 'task') for task in tasks] + [(problem, 'problem') for problem in problems]
            elif project_filter:
                # Find all tasks and problems in the project
                tasks = Task.query.join(Checkpoint).join(Milestone).filter(Milestone.project_id == project_filter).all()
                problems = Problem.query.filter_by(project_id=project_filter).all()
                results = [(task, 'task') for task in tasks] + [(problem, 'problem') for problem in problems]
        elif item_code.startswith('T'):
            # Search for specific task
            task_seq = int(item_code[1:])
            task_query = Task.query.filter_by(sequence=task_seq)

            if checkpoint_filter:
                task_query = task_query.filter_by(checkpoint_id=checkpoint_filter)

            task = task_query.first()
            if task:
                results = [(task, 'task')]
        elif item_code.upper().startswith('PB'):
            # Search for specific problem
            problem_seq = int(item_code[2:])
            problem_query = Problem.query

            if checkpoint_filter:
                problem_query = problem_query.filter_by(checkpoint_id=checkpoint_filter)
            elif milestone_filter:
                problem_query = problem_query.filter_by(milestone_id=milestone_filter)
            elif project_filter:
                problem_query = problem_query.filter_by(project_id=project_filter)

            problem_query = problem_query.filter_by(sequence=problem_seq)
            problem = problem_query.first()
            if problem:
                results = [(problem, 'problem')]

    return render_template('search_results.html', results=results, query=query)


@bp.route('/projects/filter')
@login_required
def filter_projects():
    """
    Generic project filtering view that can be used from different contexts.
    Parameters can include:
    - status: Filter by status
    - category: Filter by category
    - size: Filter by size
    - importance: Filter by importance
    """
    # Get filter parameters
    status = request.args.get('status', None)
    category = request.args.get('category', None)
    size = request.args.get('size', None)
    importance = request.args.get('importance', None)

    # Build query based on filters
    query = Project.query

    if status:
        if ',' in status:
            statuses = status.split(',')
            query = query.filter(Project.status.in_(statuses))
        else:
            query = query.filter_by(status=status)

    if category:
        query = query.filter_by(category=category)

    if size:
        query = query.filter_by(size=size)

    if importance:
        query = query.filter_by(importance=importance)

    # Execute query and get results
    projects = query.order_by(Project.created_at.desc()).all()

    title = f"Filtered Projects"
    if status:
        title = f"{status} Projects"

    # Get other data needed for dashboard
    # Count active tasks (not counting 'Pending')
    active_tasks = Task.query.filter(
        Task.assigned_to_id == current_user.id,
        Task.status.in_(['Open', 'In progress', 'On hold'])
    ).count()

    total_open_problems = Problem.query.filter(Problem.status.in_(['Open', 'In progress'])).count()
    current_date = datetime.utcnow().strftime("%Y-%m-%d")
    recent_problems = Problem.query.filter(Problem.status.in_(['Open', 'In progress'])).order_by(
        Problem.opened_at.desc()).limit(5).all()
    current_user_tasks = Task.query.filter_by(assigned_to_id=current_user.id).all()

    # Get open projects for the progress chart
    open_projects = Project.query.filter_by(status='Open').all()

    # Get user's personal notes
    personal_notes = PersonalNote.query.filter_by(user_id=current_user.id).order_by(
        PersonalNote.updated_at.desc()).all()

    # Get user's team notes from all teams they belong to
    user_teams = get_user_teams()
    team_notes = []
    for team in user_teams:
        team_notes.extend(TeamNote.query.filter_by(team_id=team.id).order_by(TeamNote.updated_at.desc()).all())

    return render_template('dashboard.html',
                           projects=projects,
                           title=title,
                           filter_active=True,
                           filter_params=request.args,
                           active_tasks=active_tasks,
                           total_open_problems=total_open_problems,
                           recent_problems=recent_problems,
                           current_user_tasks=current_user_tasks,
                           current_date=current_date,
                           open_projects=open_projects,
                           personal_notes=personal_notes,
                           team_notes=team_notes,
                           user_teams=user_teams)


@bp.route('/my-tasks')
@login_required
def my_tasks():
    """View for displaying tasks assigned to the current user"""
    # Get tasks assigned to current user with status not equal to 'Closed'
    tasks = Task.query.filter(
        Task.assigned_to_id == current_user.id,
        Task.status != 'Closed'
    ).order_by(Task.status).all()

    return render_template('my_tasks.html', tasks=tasks)