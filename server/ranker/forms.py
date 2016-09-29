from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea

class QueryForm(Form):
    query = StringField('query', validators=[DataRequired()])

class ResponseForm(Form):
    """ The fields for this form are set dynamically in the rankings view """
    pass

class EditResponseForm(Form):
    response_id = IntegerField('response_id')
    response_edited_string = StringField('response_edited_string', validators=[DataRequired()])
    delete_response = SubmitField()
    save_response = SubmitField()
    pass

class CritiqueForm(Form):
    query = StringField('query', validators=[DataRequired()], widget=TextArea())
