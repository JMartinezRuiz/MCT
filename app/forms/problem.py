"""
Forms related to problem management.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, FloatField
from wtforms.validators import DataRequired, Length

class ProblemForm(FlaskForm):
    """Form for creating and editing problems"""
    name = StringField('Problem Title', validators=[DataRequired()])
    description = TextAreaField('Problem Description')
    priority = SelectField('Priority', choices=[
        ('P1', 'P1 - Critical'),
        ('P2', 'P2 - High'),
        ('P3', 'P3 - Medium'),
        ('P4', 'P4 - Low'),
        ('P5', 'P5 - Very Low')
    ], default='P3')
    status = SelectField('Status', choices=[
        ('Open', 'Open'),
        ('In progress', 'In progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed')
    ])
    category = StringField('Category', validators=[DataRequired()])
    assigned_to = SelectField('Assigned to', coerce=int, validators=[DataRequired()])
    cost = FloatField('Cost', default=0.0)
    submit = SubmitField('Save Problem')


class ProblemCommentForm(FlaskForm):
    """Form for adding comments to problems"""
    comment_text = TextAreaField('Comment', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Add Comment')