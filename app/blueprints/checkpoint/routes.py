"""
Routes for checkpoint management functionality.
"""
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.blueprints.checkpoint import bp
from app.models.milestone import Milestone
from app.models.checkpoint import Checkpoint, CheckpointLog
from app.models.problem import Problem, ProblemComment
from app.forms.checkpoint import CheckpointForm
from app.forms.problem import ProblemForm
from app.models.user import User
from app.utils.formatting import format_work_time
from app.utils.project import get_problem_count, update_project_cost


@bp.route('/project/<int:project_id>/milestone/<int:milestone_id>/checkpoint/new', methods=['GET', 'POST'])
@login_required
def new_checkpoint(project_id, milestone_id):
    """Create a new checkpoint"""
    milestone = Milestone.query.get_or_404(milestone_id)
    if milestone.project.id != project_id:
        abort(404)
    form = CheckpointForm()
    if form.validate_on_submit():
        seq = len(milestone.checkpoints) + 1
        checkpoint = Checkpoint(name=form.name.data, description=form.description.data, milestone=milestone,
                                sequence=seq)
        db.session.add(checkpoint)
        db.session.commit()
        flash('Checkpoint created', 'success')
        return redirect(url_for('milestone.milestone_dashboard', project_id=project_id, milestone_id=milestone.id))
    return render_template('edit_checkpoint.html', form=form, checkpoint=None, milestone=milestone)


@bp.route('/project/<int:project_id>/milestone/<int:milestone_id>/checkpoint/<int:checkpoint_id>')
@login_required
def checkpoint_dashboard(project_id, milestone_id, checkpoint_id):
    """Checkpoint dashboard view"""
    checkpoint = Checkpoint.query.get_or_404(checkpoint_id)
    if checkpoint.milestone.id != milestone_id or checkpoint.milestone.project.id != project_id:
        abort(404)

    sort_by = request.args.get('sort', 'code')
    order = request.args.get('order', 'asc')

    tasks = checkpoint.tasks[:]
    try:
        tasks = sorted(tasks, key=lambda t: getattr(t, sort_by))
    except AttributeError:
        tasks = sorted(tasks, key=lambda t: t.code)
    if order == 'desc':
        tasks.reverse()

    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == 'Closed')
    open_tasks = sum(1 for t in tasks if t.status in ['Pending', 'Open', 'In progress'])
    total_work = sum(t.work_time for t in tasks)

    # Get problems for this checkpoint
    problems = Problem.query.filter_by(checkpoint_id=checkpoint_id).all()
    open_problems = [p for p in problems if p.status in ['Open', 'In progress']]

    return render_template('checkpoint_dashboard.html',
                           project_id=project_id,
                           milestone_id=milestone_id,
                           checkpoint_id=checkpoint_id,
                           checkpoint=checkpoint,
                           tasks=tasks,
                           sort_by=sort_by,
                           order=order,
                           total_tasks=total,
                           completed_tasks=completed,
                           open_tasks=open_tasks,
                           total_work_time=format_work_time(total_work),
                           problems=problems,
                           open_problems=open_problems)


@bp.route('/project/<int:project_id>/milestone/<int:milestone_id>/checkpoint/<int:checkpoint_id>/details')
@login_required
def view_checkpoint_details(project_id, milestone_id, checkpoint_id):
    """View detailed information about a checkpoint"""
    checkpoint = Checkpoint.query.get_or_404(checkpoint_id)
    if checkpoint.milestone.id != milestone_id or checkpoint.milestone.project.id != project_id:
        abort(404)

    total = len(checkpoint.tasks)
    completed = sum(1 for t in checkpoint.tasks if t.status == 'Closed')
    open_tasks = sum(1 for t in checkpoint.tasks if t.status in ['Pending', 'Open', 'In progress'])
    total_work = sum(t.work_time for t in checkpoint.tasks)

    # Get problems for this checkpoint
    problems = Problem.query.filter_by(checkpoint_id=checkpoint_id).all()

    return render_template('checkpoint_details.html',
                           checkpoint=checkpoint,
                           total_tasks=total,
                           completed_tasks=completed,
                           open_tasks=open_tasks,
                           total_work_time=format_work_time(total_work),
                           project_id=project_id,
                           milestone_id=milestone_id,
                           checkpoint_id=checkpoint_id,
                           problems=problems)


@bp.route('/project/<int:project_id>/milestone/<int:milestone_id>/checkpoint/<int:checkpoint_id>/edit',
           methods=['GET', 'POST'])
@login_required
def edit_checkpoint(project_id, milestone_id, checkpoint_id):
    """Edit checkpoint details"""
    checkpoint = Checkpoint.query.get_or_404(checkpoint_id)
    if checkpoint.milestone.id != milestone_id or checkpoint.milestone.project.id != project_id:
        abort(404)
    form = CheckpointForm(obj=checkpoint)
    if form.validate_on_submit():
        checkpoint.name = form.name.data
        checkpoint.description = form.description.data
        db.session.commit()
        flash('Checkpoint updated', 'success')
        return redirect(url_for('checkpoint.checkpoint_dashboard', project_id=project_id, milestone_id=milestone_id,
                                checkpoint_id=checkpoint.id))
    return render_template('edit_checkpoint.html', form=form, checkpoint=checkpoint, milestone=checkpoint.milestone)


@bp.route('/project/<int:project_id>/milestone/<int:milestone_id>/checkpoint/<int:checkpoint_id>/add_log',
           methods=['POST'])
@login_required
def add_checkpoint_log(project_id, milestone_id, checkpoint_id):
    """Add a log entry to a checkpoint"""
    checkpoint = Checkpoint.query.get_or_404(checkpoint_id)
    comment_text = request.form.get('comment_text')
    if comment_text:
        log = CheckpointLog(checkpoint=checkpoint, comment_text=comment_text, user_id=current_user.id)
        db.session.add(log)
        db.session.commit()
        flash('Log entry added', 'success')
    return redirect(
        url_for('checkpoint.checkpoint_dashboard', project_id=project_id, milestone_id=milestone_id, checkpoint_id=checkpoint_id))


@bp.route('/project/<int:project_id>/milestone/<int:milestone_id>/checkpoint/<int:checkpoint_id>/problem/new',
           methods=['GET', 'POST'])
@login_required
def new_checkpoint_problem(project_id, milestone_id, checkpoint_id):
    """Create a new problem at checkpoint level"""
    checkpoint = Checkpoint.query.get_or_404(checkpoint_id)
    if checkpoint.milestone.id != milestone_id or checkpoint.milestone.project.id != project_id:
        abort(404)

    form = ProblemForm()
    form.assigned_to.choices = [(u.id, u.username) for u in User.query.all()]

    if form.validate_on_submit():
        # Get sequence number for this checkpoint
        checkpoint_problems_count = Problem.query.filter_by(checkpoint_id=checkpoint_id).count()
        seq = checkpoint_problems_count + 1

        problem = Problem(
            project_id=project_id,
            milestone_id=milestone_id,
            checkpoint_id=checkpoint_id,
            name=form.name.data,
            description=form.description.data,
            priority=form.priority.data,
            status=form.status.data,
            cost=form.cost.data,
            category=form.category.data,
            assigned_to_id=form.assigned_to.data,
            sequence=seq
        )

        db.session.add(problem)

        # Add system comment for problem creation
        if problem.status in ['Open', 'In progress']:
            system_comment = ProblemComment(
                problem=problem,
                comment_text=f"Problem opened with status: {problem.status}",
                is_system=True
            )
            db.session.add(system_comment)

        db.session.commit()

        # Update project cost
        update_project_cost(project_id)

        flash('Problem created', 'success')
        return redirect(url_for('checkpoint.checkpoint_dashboard',
                                project_id=project_id,
                                milestone_id=milestone_id,
                                checkpoint_id=checkpoint_id))

    return render_template('edit_problem.html', form=form, problem=None,
                           project=checkpoint.milestone.project,
                           milestone=checkpoint.milestone,
                           checkpoint=checkpoint)