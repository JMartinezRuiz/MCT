"""
Forms related to task management.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length

class TaskForm(FlaskForm):
    """Form for creating and editing tasks"""
    name = StringField('Task Short Description', validators=[DataRequired()])
    description = TextAreaField('Task Description')
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'),
        ('Open', 'Open'),
        ('In progress', 'In progress'),
        ('Closed', 'Closed'),
        ('On hold', 'On hold')
    ])
    size = SelectField('Size', choices=[
        ('S1', 'S1'),
        ('S2', 'S2'),
        ('S3', 'S3'),
        ('S4', 'S4'),
        ('S5', 'S5')
    ])
    category = StringField('Category', validators=[DataRequired()])
    subcategory = StringField('Subcategory', validators=[DataRequired()])
    assigned_to = SelectField('Assigned to', coerce=int, validators=[DataRequired()])
    cost = FloatField('Cost', default=0.0)
    in_conditions = SelectMultipleField('In Conditions', coerce=int, choices=[])
    submit = SubmitField('Save Task')


class CommentForm(FlaskForm):
    """Form for adding comments to tasks"""
    comment_text = TextAreaField('Comment', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Add Comment')