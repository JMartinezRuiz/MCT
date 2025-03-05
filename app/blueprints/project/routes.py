"""
Routes for project management functionality.
"""
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime

from app.extensions import db
from app.blueprints.project import bp
from app.models.project import Project, ProjectLog
from app.models.milestone import Milestone
from app.models.checkpoint import Checkpoint
from app.models.task import Task
from app.models.problem import Problem

from app.forms.project import ProjectForm, ProjectStatusForm, ProjectLogForm
from app.utils.formatting import format_work_time
from app.utils.project import get_problem_count, update_project_cost


@bp.route('/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    """Create a new project"""
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            subcategory=form.subcategory.data,
            size=form.size.data,
            importance=form.importance.data,
            status=form.status.data,
            budget=form.budget.data
        )
        db.session.add(project)
        db.session.commit()

        # Add system log entry for project creation
        log_entry = ProjectLog(
            project=project,
            comment_text=f"Project created with status: {project.status}",
            is_system=True
        )
        db.session.add(log_entry)
        db.session.commit()

        flash('Project created successfully', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('edit_project.html', form=form, project=None)


@bp.route('/project/<int:project_id>')
@login_required
def project_dashboard(project_id):
    """Project dashboard view"""
    project = Project.query.get_or_404(project_id)

    # Calculate totals
    total = sum(len(cp.tasks) for m in project.milestones for cp in m.checkpoints)
    pending = sum(sum(1 for t in cp.tasks if t.status in ['Pending', 'Open', 'In progress'])
                  for m in project.milestones for cp in m.checkpoints)
    work = sum(t.work_time for m in project.milestones for cp in m.checkpoints for t in cp.tasks)

    # Get project problems and problems in its milestones/checkpoints
    direct_problems = Problem.query.filter_by(project_id=project_id, milestone_id=None, checkpoint_id=None).all()

    milestone_problems = Problem.query.join(Milestone).filter(
        Milestone.project_id == project_id,
        Problem.checkpoint_id == None
    ).all()

    checkpoint_problems = Problem.query.join(Checkpoint).join(Milestone).filter(
        Milestone.project_id == project_id
    ).all()

    all_problems = direct_problems + milestone_problems + checkpoint_problems
    open_problems = [p for p in all_problems if p.status in ['Open', 'In progress']]

    # Get recent logs (5 most recent by default)
    show_all_logs = request.args.get('all_logs', 'false') == 'true'
    if show_all_logs:
        logs = ProjectLog.query.filter_by(project_id=project_id).order_by(ProjectLog.created_at.desc()).all()
    else:
        logs = ProjectLog.query.filter_by(project_id=project_id).order_by(ProjectLog.created_at.desc()).limit(5).all()

    # Calculate if over budget
    is_over_budget = project.total_cost > project.budget if project.budget > 0 else False

    return render_template('project_dashboard.html',
                           project=project,
                           total_tasks=total,
                           pending_tasks=pending,
                           total_work_time=format_work_time(work),
                           direct_problems=direct_problems,
                           all_problems=all_problems,
                           open_problems=open_problems,
                           logs=logs,
                           show_all_logs=show_all_logs,
                           is_over_budget=is_over_budget,
                           project_id=project_id)


@bp.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """Edit project details"""
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        old_status = project.status

        project.name = form.name.data
        project.description = form.description.data
        project.category = form.category.data
        project.subcategory = form.subcategory.data
        project.size = form.size.data
        project.importance = form.importance.data
        project.budget = form.budget.data

        # Check if status changed
        if old_status != form.status.data:
            project.status = form.status.data

            # Add system log for status change
            log_entry = ProjectLog(
                project=project,
                user_id=current_user.id,
                comment_text=f"Status changed from {old_status} to {project.status}",
                is_system=True
            )
            db.session.add(log_entry)
        else:
            project.status = form.status.data

        db.session.commit()
        flash('Project updated', 'success')
        return redirect(url_for('project.project_dashboard', project_id=project.id))

    return render_template('edit_project.html', form=form, project=project)


@bp.route('/project/<int:project_id>/status', methods=['GET', 'POST'])
@login_required
def update_project_status(project_id):
    """Update project status with comment"""
    project = Project.query.get_or_404(project_id)
    form = ProjectStatusForm(obj=project)

    if form.validate_on_submit():
        old_status = project.status
        project.status = form.status.data

        # Add log entry for status change
        log_entry = ProjectLog(
            project=project,
            user_id=current_user.id,
            comment_text=f"Status changed from {old_status} to {project.status}: {form.comment.data}",
            is_system=False
        )
        db.session.add(log_entry)
        db.session.commit()

        flash('Project status updated', 'success')
        return redirect(url_for('project.project_dashboard', project_id=project.id))

    return render_template('update_project_status.html', form=form, project=project)


@bp.route('/project/<int:project_id>/log', methods=['POST'])
@login_required
def add_project_log(project_id):
    """Add a log entry to a project"""
    project = Project.query.get_or_404(project_id)
    comment_text = request.form.get('comment_text')

    if comment_text:
        log = ProjectLog(
            project=project,
            comment_text=comment_text,
            user_id=current_user.id,
            is_system=False
        )
        db.session.add(log)
        db.session.commit()
        flash('Log entry added', 'success')

    return redirect(url_for('project.project_dashboard', project_id=project.id))


@bp.route('/project/<int:project_id>/problem/new', methods=['GET', 'POST'])
@login_required
def new_project_problem(project_id):
    """Create a new problem at the project level"""
    from app.forms.problem import ProblemForm
    from app.models.user import User
    from app.models.problem import Problem, ProblemComment

    project = Project.query.get_or_404(project_id)
    form = ProblemForm()
    form.assigned_to.choices = [(u.id, u.username) for u in User.query.all()]

    if form.validate_on_submit():
        # Get sequence number for this project
        project_problems_count = Problem.query.filter_by(project_id=project_id, milestone_id=None,
                                                         checkpoint_id=None).count()
        seq = project_problems_count + 1

        problem = Problem(
            project_id=project_id,
            milestone_id=None,
            checkpoint_id=None,
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
        return redirect(url_for('project.project_dashboard', project_id=project_id))

    return render_template('edit_problem.html', form=form, problem=None,
                           project=project, milestone=None, checkpoint=None)