"""
Authentication forms including login and user settings.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, Optional

class LoginForm(FlaskForm):
    """Login form for user authentication"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class UserSettingsForm(FlaskForm):
    """User profile settings form"""
    username = StringField('Username', validators=[DataRequired()], render_kw={'readonly': True})
    email = StringField('Email', validators=[Optional(), Email()])
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    phone = StringField('Phone Number')
    profile_image = SelectField('Profile Image')
    submit = SubmitField('Save Settings')