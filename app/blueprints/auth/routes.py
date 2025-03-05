"""
Authentication routes for login/logout and user profile management.
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse

from app.extensions import db
from app.models.user import User
from app.forms.auth import LoginForm, UserSettingsForm
from app.blueprints.auth import bp


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash('Login successful', 'success')
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('main.dashboard')
            return redirect(next_page)
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/user/settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    """User profile settings page"""
    form = UserSettingsForm(obj=current_user)

    # Define available profile images
    profile_images = [
        ('avatar1.png', 'Avatar 1'),
        ('avatar2.png', 'Avatar 2'),
        ('avatar3.png', 'Avatar 3'),
        ('avatar4.png', 'Avatar 4'),
        ('avatar5.png', 'Avatar 5'),
        ('avatar6.png', 'Avatar 6')
    ]

    form.profile_image.choices = profile_images

    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        current_user.profile_image = form.profile_image.data

        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('auth.user_settings'))

    return render_template('user_settings.html', form=form, profile_images=profile_images)