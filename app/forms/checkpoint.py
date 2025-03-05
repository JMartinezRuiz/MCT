"""
Forms related to checkpoint management.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class CheckpointForm(FlaskForm):
    """Form for creating and editing checkpoints"""
    name = StringField('Checkpoint (Short Description)', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Save Checkpoint')