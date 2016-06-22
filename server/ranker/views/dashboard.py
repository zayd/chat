import sys
from ranker import forms
from ranker import app
from ranker import cg
from ranker import mongo

sys.path.insert(0, '../../')
from src import config

from flask import Blueprint, render_template, flash
import flask

from wtforms import RadioField

dashboard = Blueprint('dashboard', __name__, template_folder='templates', static_folder='bower_components')

@dashboard.route('/dashboard')
@dashboard.route('/dashboard/index.html')
def index():
    user = {}
    return render_template('dashboard/pages/index.html', user=user, title='Dashboard')

@dashboard.route('/dashboard/ranking', methods=['GET', 'POST'])
def ranking():
    """
    example_1 = {'id': 0, 'text': 'This is a test', 'score_0': 34.3, 'score_1': 23.1}
    example_2 = {'id': 1, 'text': 'This is the second test', 'score_0': 97.4, 'score_1': 32.3}
    responses = [example_1, example_2]
    """
    labels = ['Id', 'Responses', 'Score', 'Relevant?']
    responses = []

    form = forms.QueryForm()

    if form.validate_on_submit():
        app.logger.info('Query submitted: {0}'.format(form.query.data))
        responses = cg.generate_response(form.query.data)
        #mongo.db['queries'].insert(form.query.data)


    for idx, response in enumerate(responses):
        rf = RadioField('response_' + str(idx), choices=[('Yes', 'Yes'), ('No', 'No'), ('?', '?')],
                        default='?')
        setattr(forms.ResponseForm, 'response_' + str(idx), rf)

    response_form = forms.ResponseForm()

    if response_form.validate_on_submit():
        app.logger.info('Correction submitted: {0}'.format(response_form.data))
        #last_query = mongo.db['queries'].find().sort({'$natural':-1}).limit(1)
        #print last_query
        #correction_tuple = form.
        #mongo.db['corrections'].insert(correction_tuple)


    user = {'num_conversations': 5423,
            'labels': labels,
            'responses': responses}
    return render_template('dashboard/pages/ranking.html', user=user, title='Ranking', form=form, response_form=response_form)


@dashboard.route('/dashboard/grading', methods=['GET', 'POST'])
def grading():
    essay = "<p>Arthur Miller's novel, 'The Crucible,' takes place in early Salem, Massachusetts, where the use of fear was used to control anyone to blame another of witchcraft. The vindictive Abigail Williams set out to destroy the life of Elizabeth Proctor, and in doing so, created a chaos full of lies and fear in Salem. Throughout the play, basic human rights are often endangered due to fear. Today, endangerments to human rights are still the consequences of unnecessary fears. </p> <p> The first example of human rights endangered through fear is when elderly Giles Corey was stoned to death. Giles showed the court proof that the accusation of witchcraft on his wife was based on Thomas Putnam's greed for a neighbor's piece of land. This backfires and he is condemned and destined to hang. When Judge Danforth brings up his contempt of court, Giles replies, \"This is a hearing. You cannot arrest me for contempt of a hearing\" (IV.186). When he neither confesses nor denies the charges of witchcraft, he is brutally tortured; crushed with heavy stones placed on his chest. Since Salem feared witchcraft, Giles lost his human rights, thus leading to an unjust and cruel punishment. </p> <p> Another example of the intertwining of fear and human rights was the unfair treatment of those accused of witchcraft. After hearing of the trials, Elizabeth Proctor says to her husband John, \"And they'll be tried, and the court have power to hang them too..they'll hang if they'll not confess, John\" (II.49,52). This statement referred to the fact that 'justice' in the witchcraft trials meant confessing-the innocent were forced to confess if they wanted to live. Because the people of Salem were fearful of witches and their judgment was impaired, human rights were consistently violated. </p>"
    labels = ['Id', 'Responses', 'Score #0', 'Relevant?']
    responses = []

    form = forms.QueryForm()

    if form.validate_on_submit():
        app.logger.info('Query submitted: {0}'.format(form.query.data))
        responses = cg.generate_response(form.query.data)

    for idx, response in enumerate(responses):
        rf = RadioField('response_' + str(idx), choices=[('Yes', 'Yes'), ('No', 'No'), ('?', '?')],
                        default='?')
        setattr(forms.ResponseForm, 'response_' + str(idx), rf)

    response_form = forms.ResponseForm()

    if response_form.validate_on_submit():
        app.logger.info('Correction submitted: {0}'.format(response_form.data))

    user = {'num_conversations': 102,
            'labels': labels,
            'responses': responses}
    return render_template('dashboard/pages/grading.html', user=user, title='Grading', form=form, response_form=response_form, essay=essay)

