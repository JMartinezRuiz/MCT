"""
Forms related to search functionality.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    """Form for global search functionality"""
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')