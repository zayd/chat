from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class QueryForm(Form):
    query = StringField('query', validators=[DataRequired()])

class ResponseForm(Form):
    """ The fields for this form are set dynamically in the rankings view """
    pass
