from flask import Blueprint

bp = Blueprint('task', __name__)

from app.blueprints.task import routes