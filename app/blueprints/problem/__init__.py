from flask import Blueprint

bp = Blueprint('problem', __name__)

from app.blueprints.problem import routes