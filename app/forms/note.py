"""
Forms related to personal and team notes management.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length

class PersonalNoteForm(FlaskForm):
    """Form for creating and editing personal notes"""
    id = HiddenField('Note ID')
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    color = SelectField('Color', choices=[
        ('yellow', 'Yellow'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('pink', 'Pink'),
        ('purple', 'Purple'),
        ('gray', 'Gray')
    ], default='yellow')
    submit = SubmitField('Save Note')


class TeamNoteForm(FlaskForm):
    """Form for creating and editing team notes"""
    id = HiddenField('Note ID')
    team_id = SelectField('Team', coerce=int, validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    color = SelectField('Color', choices=[
        ('blue', 'Blue'),
        ('yellow', 'Yellow'),
        ('green', 'Green'),
        ('pink', 'Pink'),
        ('purple', 'Purple'),
        ('gray', 'Gray')
    ], default='blue')
    submit = SubmitField('Save Note')


class TeamForm(FlaskForm):
    """Form for creating and editing teams"""
    name = StringField('Team Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    members = SelectMultipleField('Team Members', coerce=int, choices=[])
    submit = SubmitField('Save Team')