"""
Routes for task management functionality.
"""
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.blueprints.task import bp
from app.models.user import User
from app.models.checkpoint import Checkpoint
from app.models.task import Task, Comment
from app.forms.task import TaskForm, CommentForm
from app.utils.project import update_project_cost


@bp.route('/project/<int:project_id>/milestone/<int:milestone_id>/checkpoint/<int:checkpoint_id>/task/new',
           methods=['GET', 'POST'])
@login_required
def new_task(project_id, milestone_id, checkpoint_id):
    """Create a new task in a checkpoint"""
    checkpoint = Checkpoint.query.get_or_404(checkpoint_id)
    if checkpoint.milestone.id != milestone_id or checkpoint.milestone.project.id != project_id:
        abort(404)

    form = TaskForm()
    form.assigned_to.choices = [(u.id, u.username) for u in User.query.all()]
    form.in_conditions.choices = [(t.id, t.code) for t in checkpoint.tasks]

    if form.validate_on_submit():
        seq = len(checkpoint.tasks) + 1
        task = Task(
            name=form.name.data,
            description=form.description.data,
            status=form.status.data,
            size=form.size.data,
            cost=form.cost.data,
            category=form.category.data,
            subcategory=form.subcategory.data,
            assigned_to_id=form.assigned_to.data,
            checkpoint=checkpoint,
            sequence=seq
        )

        for cond_id in form.in_conditions.data:
            required_task = Task.query.get(cond_id)
            if required_task:
                task.in_conditions.append(required_task)

        if task.status in ['Open', 'In progress']:
            task.opened_at = datetime.utcnow()
            sys_comment = Comment(task=task, comment_text="Task opened", is_system=True)
            db.session.add(sys_comment)

        db.session.add(task)
        db.session.commit()

        # Update project cost
        update_project_cost(project_id)

        flash('Task created', 'success')
        return redirect(url_for('checkpoint.checkpoint_dashboard', project_id=project_id, milestone_id=milestone_id,
                                checkpoint_id=checkpoint.id))

    return render_template('edit_task.html', form=form, task=None, checkpoint=checkpoint)


@bp.route('/project/<int:project_id>/milestone/<int:milestone_id>/checkpoint/<int:checkpoint_id>/task/<int:task_id>',
           methods=['GET', 'POST'])
@login_required
def task_detail(project_id, milestone_id, checkpoint_id, task_id):
    """View and edit task details"""
    task = Task.query.filter_by(id=task_id, checkpoint_id=checkpoint_id).first_or_404()
    if task.checkpoint.milestone.id != milestone_id or task.checkpoint.milestone.project.id != project_id:
        abort(404)

    if request.method == 'POST':
        previous_status = task.status
        old_cost = task.cost

        task.category = request.form.get('category')
        task.subcategory = request.form.get('subcategory')
        task.size = request.form.get('size')
        task.cost = float(request.form.get('cost', 0))

        assigned_to = request.form.get('assigned_to')
        if assigned_to:
            task.assigned_to_id = int(assigned_to)

        new_status = request.form.get('status')
        if new_status in ['Open', 'In progress']:
            for cond in task.in_conditions:
                if cond.status != 'Closed':
                    flash("Cannot open task. Condition " + cond.code + " not met.", "danger")
                    return redirect(url_for('task.task_detail', project_id=project_id, milestone_id=milestone_id,
                                            checkpoint_id=checkpoint_id, task_id=task.id))

        if previous_status != new_status:
            if new_status in ['Open', 'In progress'] and not task.opened_at:
                task.opened_at = datetime.utcnow()
                sys_comment = Comment(task=task, comment_text="Task opened", is_system=True)
                db.session.add(sys_comment)
            elif previous_status in ['Open', 'In progress'] and new_status not in ['Open',
                                                                                   'In progress'] and task.opened_at:
                delta = datetime.utcnow() - task.opened_at
                task.work_time += int(delta.total_seconds())
                task.opened_at = None

            sys_comment = Comment(task=task, comment_text=f"Status changed from {previous_status} to {new_status}",
                                  is_system=True)
            db.session.add(sys_comment)

        task.status = new_status
        task.name = request.form.get('name')
        task.description = request.form.get('description')

        db.session.commit()

        # Update project cost if the cost has changed
        if old_cost != task.cost:
            update_project_cost(project_id)

        flash('Task updated', 'success')
        return redirect(
            url_for('task.task_detail', project_id=project_id, milestone_id=milestone_id, checkpoint_id=checkpoint_id,
                    task_id=task.id))

    users = User.query.all()
    return render_template('task_detail.html', task=task, users=users, project_id=project_id, milestone_id=milestone_id,
                           checkpoint_id=checkpoint_id)


@bp.route(
    '/project/<int:project_id>/milestone/<int:milestone_id>/checkpoint/<int:checkpoint_id>/task/<int:task_id>/add_comment',
    methods=['POST'])
@login_required
def add_comment(project_id, milestone_id, checkpoint_id, task_id):
    """Add a comment to a task"""
    task = Task.query.filter_by(id=task_id, checkpoint_id=checkpoint_id).first_or_404()
    comment_text = request.form.get('comment_text')
    if comment_text:
        comment = Comment(task=task, comment_text=comment_text, user_id=current_user.id, is_system=False)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added', 'success')
    return redirect(
        url_for('task.task_detail', project_id=project_id, milestone_id=milestone_id, checkpoint_id=checkpoint_id,
                task_id=task.id))


@bp.route('/tasks/filter')
@login_required
def filter_tasks():
    """
    Generic task filtering view that can be used from different contexts
    Parameters can include:
    - project_id: Filter by project
    - milestone_id: Filter by milestone
    - checkpoint_id: Filter by checkpoint (required)
    - status: Filter by status
    - size: Filter by size
    - assigned_to_id: Filter by assignment
    """
    # Get filter parameters
    project_id = request.args.get('project_id', None, type=int)
    milestone_id = request.args.get('milestone_id', None, type=int)
    checkpoint_id = request.args.get('checkpoint_id', None, type=int)
    status = request.args.get('status', None)
    size = request.args.get('size', None)
    assigned_to_id = request.args.get('assigned_to_id', None, type=int)

    # For tasks, we need at least a checkpoint to scope the view
    if not checkpoint_id:
        flash('Checkpoint ID is required for task filtering', 'warning')
        return redirect(url_for('main.dashboard'))

    checkpoint = Checkpoint.query.get_or_404(checkpoint_id)
    if not milestone_id:
        milestone_id = checkpoint.milestone_id
    if not project_id:
        project_id = checkpoint.milestone.project_id

    # Build query based on filters
    query = Task.query.filter_by(checkpoint_id=checkpoint_id)

    if status:
        if ',' in status:
            statuses = status.split(',')
            query = query.filter(Task.status.in_(statuses))
        else:
            query = query.filter_by(status=status)

    if size:
        if ',' in size:
            sizes = size.split(',')
            query = query.filter(Task.size.in_(sizes))
        else:
            query = query.filter_by(size=size)

    if assigned_to_id is not None:
        query = query.filter_by(assigned_to_id=assigned_to_id)

    # Redirect to checkpoint dashboard with sort params
    sort_by = request.args.get('sort', 'code')
    order = request.args.get('order', 'asc')

    return redirect(url_for('checkpoint.checkpoint_dashboard',
                            project_id=project_id,
                            milestone_id=milestone_id,
                            checkpoint_id=checkpoint_id,
                            sort=sort_by,
                            order=order))