from flask import Blueprint

bp = Blueprint('checkpoint', __name__)

from app.blueprints.checkpoint import routes