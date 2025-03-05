"""
Forms related to milestone management.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class MilestoneForm(FlaskForm):
    """Form for creating and editing milestones"""
    name = StringField('Milestone Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Save Milestone')