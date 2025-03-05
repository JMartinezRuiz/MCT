"""
Routes for milestone management functionality.
"""
from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.blueprints.milestone import bp
from app.models.project import Project
from app.models.milestone import Milestone
from app.models.problem import Problem
from app.forms.milestone import MilestoneForm
from app.utils.project import compute_milestone_status, get_problem_count
from app.utils.formatting import milestone_color
from app.forms.problem import ProblemForm
from app.models.user import User
from app.models.problem import ProblemComment


@bp.route('/project/<int:project_id>/milestone/new', methods=['GET', 'POST'])
@login_required
def new_milestone(project_id):
    """Create a new milestone"""
    project = Project.query.get_or_404(project_id)
    form = MilestoneForm()
    if form.validate_on_submit():
        seq = len(project.milestones) + 1
        milestone = Milestone(name=form.name.data, description=form.description.data, project=project, sequence=seq)
        db.session.add(milestone)
        db.session.commit()
        flash('Milestone created', 'success')
        return redirect(url_for('milestone.milestone_dashboard', project_id=project.id, milestone_id=milestone.id))
    return render_template('edit_milestone.html', form=form, milestone=None, project=project)


@bp.route('/project/<int:project_id>/milestone/<int:milestone_id>')
@login_required
def milestone_dashboard(project_id, milestone_id):
    """Milestone dashboard view"""
    milestone = Milestone.query.get_or_404(milestone_id)
    if milestone.project.id != project_id:
        abort(404)

    status = compute_milestone_status(milestone)
    color = milestone_color(status)
    total = sum(len(cp.tasks) for cp in milestone.checkpoints)
    closed = sum(sum(1 for t in cp.tasks if t.status == 'Closed') for cp in milestone.checkpoints)
    progress = int((closed / total) * 100) if total > 0 else 0

    # Get problems for this milestone and its checkpoints
    direct_problems = Problem.query.filter_by(milestone_id=milestone_id, checkpoint_id=None).all()

    checkpoint_problems = Problem.query.join(Checkpoint).filter(
        Checkpoint.milestone_id == milestone_id
    ).all()

    all_problems = direct_problems + checkpoint_problems
    open_problems = [p for p in all_problems if p.status in ['Open', 'In progress']]

    return render_template('milestone_dashboard.html',
                           milestone=milestone,
                           status=status,
                           color=color,
                           progress=progress,
                           project_id=project_id,
                           milestone_id=milestone_id,
                           direct_problems=direct_problems,
                           all_problems=all_problems,
                           open_problems=open_problems)


@bp.route('/project/<int:project_id>/milestone/<int:milestone_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_milestone(project_id, milestone_id):
    """Edit milestone details"""
    milestone = Milestone.query.get_or_404(milestone_id)
    if milestone.project.id != project_id:
        abort(404)
    form = MilestoneForm(obj=milestone)
    if form.validate_on_submit():
        milestone.name = form.name.data
        milestone.description = form.description.data
        db.session.commit()
        flash('Milestone updated', 'success')
        return redirect(url_for('project.project_dashboard', project_id=project_id))
    return render_template('edit_milestone.html', form=form, milestone=milestone, project=milestone.project)


@bp.route('/project/<int:project_id>/milestone/<int:milestone_id>/problem/new', methods=['GET', 'POST'])
@login_required
def new_milestone_problem(project_id, milestone_id):
    """Create a new problem at milestone level"""
    milestone = Milestone.query.get_or_404(milestone_id)
    if milestone.project.id != project_id:
        abort(404)

    form = ProblemForm()
    form.assigned_to.choices = [(u.id, u.username) for u in User.query.all()]

    if form.validate_on_submit():
        # Get sequence number for this milestone
        milestone_problems_count = Problem.query.filter_by(milestone_id=milestone_id, checkpoint_id=None).count()
        seq = milestone_problems_count + 1

        problem = Problem(
            project_id=project_id,
            milestone_id=milestone_id,
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
        from app.utils.project import update_project_cost
        update_project_cost(project_id)

        flash('Problem created', 'success')
        return redirect(url_for('milestone.milestone_dashboard', project_id=project_id, milestone_id=milestone_id))

    return render_template('edit_problem.html', form=form, problem=None,
                           project=milestone.project, milestone=milestone, checkpoint=None)