from flask import Blueprint

bp = Blueprint('milestone', __name__)

from app.blueprints.milestone import routes