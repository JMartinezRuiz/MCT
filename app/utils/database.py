"""
Database utility functions for maintenance and setup.
"""
from sqlalchemy import inspect, text
from datetime import datetime

from app.extensions import db
from app.models.user import User
from app.models.team import Team


def update_database_structure():
    """
    Updates the database structure for backwards compatibility.
    Checks for missing columns and tables and adds them as needed.
    """
    try:
        # Check if new columns and tables exist
        inspector = inspect(db.engine)

        # Check if the Problem table exists
        if 'problem' not in inspector.get_table_names():
            # Create necessary tables
            print("Creating new tables...")
            db.create_all()

        # Update project table if needed
        if 'project' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('project')]

            # Add status column if it doesn't exist
            if 'status' not in columns:
                db.session.execute(text('ALTER TABLE project ADD COLUMN status VARCHAR(20) DEFAULT "Planning"'))
                db.session.commit()
                print('Field status added to project table')

            # Add budget column if it doesn't exist
            if 'budget' not in columns:
                db.session.execute(text('ALTER TABLE project ADD COLUMN budget FLOAT DEFAULT 0.0'))
                db.session.commit()
                print('Field budget added to project table')

            # Add total_cost column if it doesn't exist
            if 'total_cost' not in columns:
                db.session.execute(text('ALTER TABLE project ADD COLUMN total_cost FLOAT DEFAULT 0.0'))
                db.session.commit()
                print('Field total_cost added to project table')

            # Add subcategory column if it doesn't exist
            if 'subcategory' not in columns:
                db.session.execute(text('ALTER TABLE project ADD COLUMN subcategory VARCHAR(50)'))
                db.session.commit()
                print('Field subcategory added to project table')

            # Add size column if it doesn't exist
            if 'size' not in columns:
                db.session.execute(text('ALTER TABLE project ADD COLUMN size VARCHAR(2) DEFAULT "S3"'))
                db.session.commit()
                print('Field size added to project table')

        # Update task table if needed
        if 'task' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('task')]

            # Add cost column if it doesn't exist
            if 'cost' not in columns:
                db.session.execute(text('ALTER TABLE task ADD COLUMN cost FLOAT DEFAULT 0.0'))
                db.session.commit()
                print('Field cost added to task table')

        # Update user table if needed
        if 'user' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('user')]

            # Add email column if it doesn't exist
            if 'email' not in columns:
                db.session.execute(text('ALTER TABLE user ADD COLUMN email VARCHAR(120) DEFAULT NULL'))
                db.session.commit()
                print('Field email added to user table')

            # Add first_name column if it doesn't exist
            if 'first_name' not in columns:
                db.session.execute(text('ALTER TABLE user ADD COLUMN first_name VARCHAR(80) DEFAULT NULL'))
                db.session.commit()
                print('Field first_name added to user table')

            # Add last_name column if it doesn't exist
            if 'last_name' not in columns:
                db.session.execute(text('ALTER TABLE user ADD COLUMN last_name VARCHAR(80) DEFAULT NULL'))
                db.session.commit()
                print('Field last_name added to user table')

            # Add phone column if it doesn't exist
            if 'phone' not in columns:
                db.session.execute(text('ALTER TABLE user ADD COLUMN phone VARCHAR(20) DEFAULT NULL'))
                db.session.commit()
                print('Field phone added to user table')

            # Add profile_image column if it doesn't exist
            if 'profile_image' not in columns:
                db.session.execute(text('ALTER TABLE user ADD COLUMN profile_image VARCHAR(120) DEFAULT "avatar1.png"'))
                db.session.commit()
                print('Field profile_image added to user table')

        # Check if the ProjectDocument table exists
        if 'project_document' not in inspector.get_table_names():
            db.create_all()
            print("Created ProjectDocument table")
        else:
            # Check if title column exists in ProjectDocument
            columns = [col['name'] for col in inspector.get_columns('project_document')]
            if 'title' not in columns:
                db.session.execute(
                    text('ALTER TABLE project_document ADD COLUMN title VARCHAR(255) NOT NULL DEFAULT "Untitled"'))

                # If the name column exists, migrate data
                if 'name' in columns:
                    db.session.execute(text('UPDATE project_document SET title = name'))

                db.session.commit()
                print('Added title column to project_document table')

        # Check if team, personal_note and team_note tables exist
        if 'team' not in inspector.get_table_names() or 'personal_note' not in inspector.get_table_names() or 'team_note' not in inspector.get_table_names():
            db.create_all()
            print("Created note-related tables")

            # Create default team if needed
            default_team = Team.query.filter_by(name="Default Team").first()
            if not default_team:
                default_team = Team(name="Default Team", description="Default team for all users")
                db.session.add(default_team)
                db.session.commit()
                print("Created default team")

        # Create user_teams association table if it doesn't exist
        if 'user_teams' not in inspector.get_table_names():
            db.session.execute(text('''
                CREATE TABLE user_teams (
                    user_id INTEGER NOT NULL,
                    team_id INTEGER NOT NULL,
                    PRIMARY KEY (user_id, team_id),
                    FOREIGN KEY(user_id) REFERENCES user (id),
                    FOREIGN KEY(team_id) REFERENCES team (id)
                )
            '''))
            db.session.commit()
            print("Created user_teams association table")

    except Exception as e:
        print(f"Error updating database structure: {str(e)}")
        db.session.rollback()


def create_default_admin():
    """
    Creates a default admin user if no admin exists.
    Also assigns the admin to the default team.
    """
    from app.models.team import Team

    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin', is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created")

        # Assign admin to default team
        default_team = Team.query.filter_by(name="Default Team").first()
        if default_team and admin not in default_team.members:
            default_team.members.append(admin)
            db.session.commit()
            print("Added admin to default team")