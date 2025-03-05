"""
API routes for AJAX functionality.
"""
from flask import jsonify, request
from flask_login import login_required

from app.extensions import db
from app.blueprints.api import bp
from app.models.project import Project
from app.models.task import Task
from app.models.problem import Problem
from app.utils.project import update_project_cost


@bp.route('/projects/open-progress', methods=['GET'])
@login_required
def get_open_projects_progress():
    """API endpoint to get progress data for open projects"""
    open_projects = Project.query.filter_by(status='Open').all()

    projects_data = [{
        'id': project.id,
        'name': project.name,
        'code': project.code,
        'progress': project.get_progress()
    } for project in open_projects]

    # Sort by progress in descending order
    projects_data = sorted(projects_data, key=lambda x: x['progress'], reverse=True)

    return jsonify(projects_data)


@bp.route('/update_task_cost', methods=['POST'])
@login_required
def update_task_cost():
    """API endpoint to update task cost"""
    task_id = request.json.get('task_id')
    new_cost = float(request.json.get('cost', 0))

    task = Task.query.get_or_404(task_id)
    task.cost = new_cost
    db.session.commit()

    # Get project ID from task's hierarchy
    project_id = task.checkpoint.milestone.project.id

    # Update project cost
    total_cost = update_project_cost(project_id)

    return jsonify({
        'success': True,
        'task_id': task_id,
        'new_cost': new_cost,
        'project_id': project_id,
        'project_total_cost': total_cost
    })


@bp.route('/update_problem_cost', methods=['POST'])
@login_required
def update_problem_cost():
    """API endpoint to update problem cost"""
    problem_id = request.json.get('problem_id')
    new_cost = float(request.json.get('cost', 0))

    problem = Problem.query.get_or_404(problem_id)
    problem.cost = new_cost
    db.session.commit()

    # Update project cost
    total_cost = update_project_cost(problem.project_id)

    return jsonify({
        'success': True,
        'problem_id': problem_id,
        'new_cost': new_cost,
        'project_id': problem.project_id,
        'project_total_cost': total_cost
    })