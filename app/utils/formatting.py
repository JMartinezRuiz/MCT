"""
Utility functions for text and data formatting.
"""
from datetime import datetime, timedelta
import markdown


def format_work_time(seconds):
    """
    Format work time in seconds to a human-readable string.

    Args:
        seconds: Time duration in seconds

    Returns:
        Formatted string representation of the time
    """
    return str(timedelta(seconds=seconds))


def render_markdown(content):
    """
    Render markdown text to HTML.

    Args:
        content: Markdown formatted text

    Returns:
        HTML formatted text or original content on error
    """
    if not content:
        return ""
    try:
        return markdown.markdown(content, extensions=['fenced_code', 'tables'])
    except:
        return content  # Return original content in case of error


def milestone_color(status):
    """
    Return Bootstrap color class based on milestone status.

    Args:
        status: Status string ('Completed', 'In progress', etc.)

    Returns:
        CSS color class name
    """
    if status == 'Completed':
        return 'success'
    elif status == 'In progress':
        return 'primary'
    else:
        return 'secondary'


def register_template_utilities(app):
    """
    Register utility functions with Jinja2 templates.

    Args:
        app: Flask application instance
    """
    from app.utils.project import compute_milestone_status, get_problem_count, get_user_projects, get_user_teams

    @app.context_processor
    def utility_processor():
        def get_user_avatar(user):
            """Get user avatar or return a default if none exists"""
            if hasattr(user, 'profile_image') and user.profile_image:
                return user.profile_image
            return 'avatar1.png'

        return dict(
            compute_milestone_status=compute_milestone_status,
            milestone_color=milestone_color,
            format_work_time=format_work_time,
            get_problem_count=get_problem_count,
            now=datetime.utcnow(),
            render_markdown=render_markdown,
            get_user_projects=get_user_projects,
            get_user_teams=get_user_teams,
            get_user_avatar=get_user_avatar
        )