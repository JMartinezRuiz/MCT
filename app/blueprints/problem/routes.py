"""
Routes for problem management functionality.
"""
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user

from app.extensions import db
from app.blueprints.problem import bp
from app.models.problem import Problem, ProblemComment
from app.models.user import User
from app.forms.problem import ProblemForm, ProblemCommentForm
from app.utils.project import update_project_cost, get_problem_count


@bp.route('/problem/<int:problem_id>')
@login_required
def problem_detail(problem_id):
    """View problem details"""
    problem = Problem.query.get_or_404(problem_id)

    # Get parent context for "back" button
    parent_type = None
    parent_id = None

    if problem.checkpoint_id:
        parent_type = 'checkpoint'
        parent_id = problem.checkpoint_id
    elif problem.milestone_id:
        parent_type = 'milestone'
        parent_id = problem.milestone_id
    else:
        parent_type = 'project'
        parent_id = problem.project_id

    # For age calculation
    from datetime import datetime
    now = datetime.utcnow()
    age_days = (now - problem.opened_at).days

    users = User.query.all()
    return render_template(
        'problem_detail.html',
        problem=problem,
        users=users,
        parent_type=parent_type,
        parent_id=parent_id,
        project_id=problem.project_id,
        milestone_id=problem.milestone_id if problem.milestone else None,
        now=now,
        age_days=age_days
    )


@bp.route('/problem/<int:problem_id>', methods=['POST'])
@login_required
def update_problem(problem_id):
    """Update problem details"""
    problem = Problem.query.get_or_404(problem_id)

    previous_status = problem.status
    old_cost = problem.cost

    # Update fields from form
    problem.name = request.form.get('name')
    problem.description = request.form.get('description')
    problem.category = request.form.get('category')
    problem.priority = request.form.get('priority')
    problem.cost = float(request.form.get('cost', 0))

    assigned_to = request.form.get('assigned_to')
    if assigned_to:
        problem.assigned_to_id = int(assigned_to)

    # Handle status changes
    new_status = request.form.get('status')
    if previous_status != new_status:
        # Add system comment for status change
        sys_comment = ProblemComment(
            problem=problem,
            comment_text=f"Status changed from {previous_status} to {new_status}",
            is_system=True
        )
        db.session.add(sys_comment)

        # Update resolution date if needed
        if new_status in ['Resolved', 'Closed'] and previous_status not in ['Resolved', 'Closed']:
            problem.resolved_at = datetime.utcnow()
        elif new_status not in ['Resolved', 'Closed'] and previous_status in ['Resolved', 'Closed']:
            problem.resolved_at = None

    problem.status = new_status
    db.session.commit()

    # Update project cost if the cost has changed
    if old_cost != problem.cost:
        update_project_cost(problem.project_id)

    flash('Problem updated', 'success')
    return redirect(url_for('problem.problem_detail', problem_id=problem.id))


@bp.route('/problem/<int:problem_id>/add_comment', methods=['POST'])
@login_required
def add_problem_comment(problem_id):
    """Add a comment to a problem"""
    problem = Problem.query.get_or_404(problem_id)
    comment_text = request.form.get('comment_text')

    if comment_text:
        comment = ProblemComment(
            problem=problem,
            comment_text=comment_text,
            user_id=current_user.id,
            is_system=False
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment added', 'success')

    return redirect(url_for('problem.problem_detail', problem_id=problem.id))


@bp.route('/problems/filter')
@login_required
def filter_problems():
    """
    Filter problems based on various criteria.
    Parameters can include:
    - project_id: Filter by project
    - milestone_id: Filter by milestone
    - checkpoint_id: Filter by checkpoint
    - status: Filter by status
    - priority: Filter by priority
    - age: Filter by age in days
    """
    # Get filter parameters
    project_id = request.args.get('project_id', None, type=int)
    milestone_id = request.args.get('milestone_id', None, type=int)
    checkpoint_id = request.args.get('checkpoint_id', None, type=int)
    status = request.args.get('status', None)
    priority = request.args.get('priority', None)
    age = request.args.get('age', None, type=int)

    # Build query based on filters
    query = Problem.query

    if project_id:
        query = query.filter_by(project_id=project_id)

    if milestone_id:
        query = query.filter_by(milestone_id=milestone_id)

    if checkpoint_id:
        query = query.filter_by(checkpoint_id=checkpoint_id)

    if status:
        if ',' in status:
            statuses = status.split(',')
            query = query.filter(Problem.status.in_(statuses))
        else:
            query = query.filter_by(status=status)

    if priority:
        if ',' in priority:
            priorities = priority.split(',')
            query = query.filter(Problem.priority.in_(priorities))
        else:
            query = query.filter_by(priority=priority)

    # Age filter requires extra calculation
    if age:
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=age)
        query = query.filter(Problem.opened_at >= cutoff_date)

    # Execute query
    problems = query.order_by(Problem.opened_at.desc()).all()

    # Get context for template
    from app.models.project import Project
    from app.models.milestone import Milestone
    from app.models.checkpoint import Checkpoint

    project = None
    milestone = None
    checkpoint = None

    if project_id:
        project = Project.query.get(project_id)

    if milestone_id:
        milestone = Milestone.query.get(milestone_id)

    if checkpoint_id:
        checkpoint = Checkpoint.query.get(checkpoint_id)

    # For age calculation
    now = datetime.utcnow()

    return render_template(
        'problems.html',
        problems=problems,
        project=project,
        milestone=milestone,
        checkpoint=checkpoint,
        now=now
    )