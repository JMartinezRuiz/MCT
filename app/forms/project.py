"""
Forms related to project management.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, FloatField
from wtforms.validators import DataRequired, Length

class ProjectForm(FlaskForm):
    """Form for creating and editing projects"""
    name = StringField('Project Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    category = SelectField('Category', choices=[
        ('Development', 'Development'),
        ('Research', 'Research'),
        ('Marketing', 'Marketing'),
        ('Infrastructure', 'Infrastructure'),
        ('Support', 'Support'),
        ('Other', 'Other')
    ])
    subcategory = StringField('Subcategory')
    size = SelectField('Size', choices=[
        ('S1', 'S1 - Very Small'),
        ('S2', 'S2 - Small'),
        ('S3', 'S3 - Medium'),
        ('S4', 'S4 - Large'),
        ('S5', 'S5 - Very Large')
    ], default='S3')
    importance = SelectField('Importance', choices=[
        ('P1', 'P1 - Critical'),
        ('P2', 'P2 - High'),
        ('P3', 'P3 - Medium'),
        ('P4', 'P4 - Low'),
        ('P5', 'P5 - Very Low')
    ], default='P5')
    status = SelectField('Status', choices=[
        ('Planning', 'Planning'),
        ('Open', 'Open'),
        ('Review', 'Review'),
        ('Closed', 'Closed')
    ], default='Planning')
    budget = FloatField('Budget', default=0.0)
    submit = SubmitField('Save Project')


class ProjectStatusForm(FlaskForm):
    """Form for updating project status"""
    status = SelectField('Status', choices=[
        ('Planning', 'Planning'),
        ('Open', 'Open'),
        ('Review', 'Review'),
        ('Closed', 'Closed')
    ])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Update Status')


class ProjectLogForm(FlaskForm):
    """Form for adding project log entries"""
    comment_text = TextAreaField('Log Entry', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Add Log Entry')


class ProjectDocumentForm(FlaskForm):
    """Form for creating and editing project documents"""
    title = StringField('Document Title', validators=[DataRequired()])
    format = SelectField('Format', choices=[
        ('md', 'Markdown'),
        ('txt', 'Plain Text')
    ], default='md')
    content = TextAreaField('Content')
    submit = SubmitField('Save Document')