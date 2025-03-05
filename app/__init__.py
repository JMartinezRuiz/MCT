import os
from flask import Flask
from app.config import Config
from app.extensions import db, login_manager


def create_app(config_class=Config):
    """Application factory function to create and configure the Flask app"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register utilities with templates
    from app.utils.formatting import register_template_utilities
    register_template_utilities(app)

    # Register blueprints
    from app.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.blueprints.project import bp as project_bp
    app.register_blueprint(project_bp)

    from app.blueprints.milestone import bp as milestone_bp
    app.register_blueprint(milestone_bp)

    from app.blueprints.checkpoint import bp as checkpoint_bp
    app.register_blueprint(checkpoint_bp)

    from app.blueprints.task import bp as task_bp
    app.register_blueprint(task_bp)

    from app.blueprints.problem import bp as problem_bp
    app.register_blueprint(problem_bp)

    from app.blueprints.document import bp as document_bp
    app.register_blueprint(document_bp)

    from app.blueprints.note import bp as note_bp
    app.register_blueprint(note_bp)

    from app.blueprints.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Ensure the upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    with app.app_context():
        # Create database if it doesn't exist
        db.create_all()

        # Update database structure
        from app.utils.database import update_database_structure
        update_database_structure()

        # Create default admin user
        from app.utils.database import create_default_admin
        create_default_admin()

    return app