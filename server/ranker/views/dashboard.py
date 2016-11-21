import string
import sys
from ranker import forms
from ranker import app
import ranker
#from ranker.tasks import cg
#from ranker import tasks
import chat_module
#from ranker.tasks import celery
from ranker import chat_db
from ranker import grading_db
from ranker import new_grading_db
import psycopg2
import markdown
import itertools
import operator
import urllib
import random
import copy 
sys.path.insert(0, '../../')
from src import config

from flask import Flask, Blueprint, render_template, flash, request, redirect, url_for
import flask
from flask.ext.login import LoginManager, UserMixin, login_required

from wtforms import RadioField, TextAreaField

# Import grading module
sys.path.insert(0, '/home/'+config.USERNAME+'/code/grading/src/')
import grading_module

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
        responses = chat_module.generate_response(form.query.data)
        #responses = cg.generate_response(form.query.data)
        #responses = tasks.run(form.query.data)
        #chat_db.db['queries'].insert(form.query.data)


    for idx, response in enumerate(responses):
        rf = RadioField('response_' + str(idx), choices=[('Yes', 'Yes'), ('No', 'No'), ('?', '?')],
                        default='?')
        setattr(forms.ResponseForm, 'response_' + str(idx), rf)

    response_form = forms.ResponseForm()

    if response_form.validate_on_submit():
        app.logger.info('Correction submitted: {0}'.format(response_form.data))
        #last_query = chat_db.db['queries'].find().sort({'$natural':-1}).limit(1)
        #print last_query
        #correction_tuple = form.
        #chat_db.db['corrections'].insert(correction_tuple)


    user = {'num_conversations': 5423,
            'labels': labels,
            'responses': responses}
    return render_template('dashboard/pages/ranking.html', user=user, title='Ranking', form=form, response_form=response_form)

@dashboard.route('/dashboard/grading', methods=['GET', 'POST'])
def grading():
    labels = ['Id', 'Responses', 'Score #0', 'Relevant?']

    q1 = {'text': 'Good job! This result means that if you always guessed that a passenger did not survive, you would be right more often than not (more often than random chance).', 'color': 'rgba(221, 119, 136, 0.15)'}
    q1_b = {'text': 'Great, you have run the code and get the correct result.', 'color': 'rgba(221, 153, 119, 0.15)'}
    q1_c = {'text': 'Well done! Results from predictions_0 has been reported correctly as 61.62%', 'color': ''}
    q1_d = {'text': 'This result means that if you always guessed that a passenger did not survive, you would be right more often than not (more often than random chance). Another way of thinking about this, is that the dataset is unbalanced.', 'color': 'rgba(102, 85, 102, 0.15)'}
    q1_wrong = {'text': 'You did not submit an answer to this question in the submission.'}
    responses = [q1, q1_b, q1_c]

    q2_a = {'text': 'This is a great example of a classification problem. You\'ll learn how to do this later in the course.'}
    q2_b = {'text': 'That is good example for problem that can be addressed by supervised learning.', 'color': 'rgba(122, 148, 96, 0.15)'}
    q2_c = {'text': 'Great example!'}
    q2_d = {'text': 'This is a very interesting and plausible supervised learning scenario, well done.'}

    all_responses = [[[q1, q1_b, q1_c], [q1_b, q1_c, q1_d], [q1_b, q1_d, q1], [q1_wrong], []],
                    [[q2_d, q2_c, q2_b], [q2_a, q2_c, q2_b], [q2_a, q2_b], [q1_wrong], []]]

    submissions = list(new_grading_db.db['submissions'].find({'answers': {'$not': {'$size': 0}}}).sort("_id", -1))

    annotations = {'highlight-pass': u"<div class=highlight-pass>{}</div>", 'highlight-fail': u"<div class=highlight-fail>{}</div>", "none":u"{}"}
    submission = random.choice(submissions)
    submission['suggestions'] = []
    grades = submission['grades']
    for jdx, answer in enumerate(submission['answers']):
        result = grades[jdx]['result']
        for cell in answer:
            lines = cell['source']
            for kdx, line in enumerate(lines):
                if(request.args.get("intelligence") != "0"):
                    lines[kdx] = annotations[line[0]].format(line[1])
                else:
                    lines[kdx] = line[1]
                    print(lines[kdx])

            cell['source'] = markdown.markdown(' '.join(lines))
        
        print submission['answers']
        if(request.args.get("intelligence") != "0"):
            suggestions = list(grading_module.generate_random_response('', 'submissions', jdx))
            #print suggestions
            ## markdown suggestions
            #for suggestion in suggestions:
            ##suggestion['text'] = markdown.markdown(''.join(suggestion['text']))
            submission['suggestions'].append(suggestions)

    form = forms.CritiqueForm()

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
    return render_template('dashboard/pages/grading.html', user=user, title='Grading', form=form, response_form=response_form, submission=submission)

@dashboard.route('/dashboard/responses', methods=['GET', 'POST'])
def responses():
    data = request.data or request.form
    print data

    question = request.args.get('question', '')

    if not question:
      user = {'question': '',
              'num_responses': 0,
              'responses': []}
      return render_template('dashboard/pages/responses.html', user=user, title='Grading')

    responses = list(grading_db.db[question].find())
    filtered_responses = list(grading_db.db['filtered-' + question].find())

    for response in responses:
      response['count'] = 1

    #responses.sort(key=operator.itemgetter('observation'))

    #filtered_responses = []
    #for key, group in itertools.groupby(responses, lambda x: x.get('observation')):
    #    response = list(group)
    #    filtered_responses.append(response[0])
    #    filtered_responses[-1]['count'] = len(response)

    #labels = filtered_responses[0].keys()

    # Generate form that will allow us to edit responses
    #for idx, response in enumerate(responses):
    #    #rf = RadioField('response_' + str(idx), choices=[('Yes', 'Yes'), ('No', 'No')],
    #    #                default='?')
    #    #setattr(forms.EditResponseForm, 'response_' + str(idx), rf)

    edit_response_forms = []
    for idx, filtered_response in enumerate(filtered_responses):
      edit_response_forms.append(forms.EditResponseForm(prefix='response' + str(idx)))

    for idx, edit_response_form in enumerate(edit_response_forms):
      response_submit = request.form.get('response' + str(idx) + 'submit')
      if response_submit == 'delete-response':
        grading_db.db['filtered-' + question].remove({'_id': filtered_responses[idx]['_id']})
        return redirect('/dashboard/responses?' + urllib.urlencode(request.args))
        #print "HAHA we are deleting", idx
      elif response_submit == 'save-response':
        response_text = request.form.get('response' + str(idx) + 'hidden')
        #print response_text, "for",  idx
        grading_db.db['filtered-' + question].update({'_id': filtered_responses[idx]['_id']},
            {'observation': response_text})
        return redirect('/dashboard/responses?' + urllib.urlencode(request.args))
      elif response_submit == 'star-response':
        starred = filtered_responses[idx].get('starred', False)
        grading_db.db['filtered-' + question].update({'_id': filtered_responses[idx]['_id']},
            {'$set': {'starred': not starred}})
        return redirect('/dashboard/responses?' + urllib.urlencode(request.args))

    user = {'question': question,
            'num_responses': len(responses),
            'responses': responses,
            'filtered_responses': filtered_responses}
    return render_template('dashboard/pages/responses.html', user=user, title='Grading', edit_response_forms=edit_response_forms)


@dashboard.route('/dashboard/evaluate', methods=['GET', 'POST'])
def evaluate():
    labels = ['Id', 'Responses', 'Score #0', 'Relevant?']

    q1 = {'text': 'Good job! This result means that if you always guessed that a passenger did not survive, you would be right more often than not (more often than random chance).', 'color': 'rgba(221, 119, 136, 0.15)'}
    q1_b = {'text': 'Great, you have run the code and get the correct result.', 'color': 'rgba(221, 153, 119, 0.15)'}
    q1_c = {'text': 'Well done! Results from predictions_0 has been reported correctly as 61.62%', 'color': ''}
    q1_d = {'text': 'This result means that if you always guessed that a passenger did not survive, you would be right more often than not (more often than random chance). Another way of thinking about this, is that the dataset is unbalanced.', 'color': 'rgba(102, 85, 102, 0.15)'}
    q1_wrong = {'text': 'You did not submit an answer to this question in the submission.'}
    responses = [q1, q1_b, q1_c]

    q2_a = {'text': 'This is a great example of a classification problem. You\'ll learn how to do this later in the course.'}
    q2_b = {'text': 'That is good example for problem that can be addressed by supervised learning.', 'color': 'rgba(122, 148, 96, 0.15)'}
    q2_c = {'text': 'Great example!'}
    q2_d = {'text': 'This is a very interesting and plausible supervised learning scenario, well done.'}

    all_responses = [[[q1, q1_b, q1_c], [q1_b, q1_c, q1_d], [q1_b, q1_d, q1], [q1_wrong], []],
                    [[q2_d, q2_c, q2_b], [q2_a, q2_c, q2_b], [q2_a, q2_b], [q1_wrong], []]]

    submissions = list(new_grading_db.db['submissions'].find({'answers': {'$not': {'$size': 0}}}).sort("_id", -1))

    annotations = {'highlight-pass': u"<div class=highlight-pass>{}</div>", 'highlight-fail': u"<div class=highlight-fail>{}</div>", "none":u"{}"}
    submission = random.choice(submissions)
    submission['suggestions'] = []
    grades = submission['grades']
    jdx = random.choice(range(len(submission['answers'])))
    answer = submission['answers'][jdx]    
    submission['answers']=answer
    result = grades[jdx]['result']
    for cell in answer:
        lines = cell['source']
        for kdx, line in enumerate(lines):
            if(request.args.get("intelligence") != "0"):
                lines[kdx] = annotations[line[0]].format(line[1])
            else:
                lines[kdx] = line[1]
                print(lines[kdx])

        cell['source'] = markdown.markdown(' '.join(lines))
    
    if(request.args.get("intelligence") != "0"):
        suggestions = list(grading_module.generate_random_response('', 'submissions', jdx))[0]
        #print suggestions
        ## markdown suggestions
        #for suggestion in suggestions:
        ##suggestion['text'] = markdown.markdown(''.join(suggestion['text']))
        submission['suggestions'].append(suggestions)

    form = forms.CritiqueForm()

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
    return render_template('dashboard/pages/evaluate.html', user=user, title='Evaluate', form=form, response_form=response_form, submission=submission)



@dashboard.route('/dashboard/deleteUser', methods=['GET', 'POST'])
def deleteUser():
    username = request.args.get('username')
    user = ranker.User.query.filter_by(email=username).all()[0]
    ranker.db.session.delete(user)
    ranker.db.session.commit()
    return redirect("/dashboard/admin")

@dashboard.route('/dashboard/admin', methods=['GET', 'POST'])
@login_required
def admin():
    conn = psycopg2.connect(dbname='responses', user='dthirman', host='udacity.cjsia33swned.us-west-1.redshift.amazonaws.com', port='5439', password='Udacity1')
    cur = conn.cursor()

    cur.execute("select original_timestamp, user_id from javascript.identifies;")

    identifies = cur.fetchall();
    try:
        username = request.form['username']
        userid = request.form['id']
        password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
        user = ranker.createUser(username, password, userid)
        ranker.db.session.add(user)
        ranker.db.session.commit()
    except Exception as e:
        print e
    responses = {}
    users = ranker.User.query.all()
    users =  [str(x.email) for x in users if x.username != u'admin']
    #users = set([x[1] for x in identifies])
    for i in identifies:
        if(i[1] is not None and '?' not in i[1]):
            if i[1] not in responses:
                responses[i[1]] = []
                if(i[1] and i[1].isdigit()):

                    stri = 'select original_timestamp, grade from javascript.entered_grade where user_id=' + i[1]+ ';'
                    cur.execute(stri)
                    grade = cur.fetchall();
                    responses[i[1]] += [['grade'] + list(x) for x in grade]

                    stri = 'select original_timestamp, type from javascript.entered_response where user_id=' + i[1]+ ';'
                    cur.execute(stri)
                    response = cur.fetchall();
                    responses[i[1]] += [['response'] + list(x) for x in response]
                    cur.execute("select original_timestamp, user_id from javascript.submitted_grade where user_id= "+ i[1]+ ';')
                    submits = cur.fetchall();
                    responses[i[1]] += [['Submitted Grade'] + list(x) for x in submits]


                    cur.execute("select original_timestamp from javascript.submitted_grade_and_next_user where context_page_search like '%id="+i[1]+"%';")
                    submitNexts = cur.fetchall();
                    for s in submitNexts:
                        if s[0] is not None:
                            responses[i[1]] += [['Submitted Grade and Moved to Next User'] + list(s)+[i[1]]]

            responses[i[1]].append(['identify'] + list(i))
    print users
    #users = [ x for x in users if x is not None and '?' not in x]
    newUsers = []
    statistics = {}
    for u in users:

        newUser = ranker.User.query.filter_by(email=u).all()
        if(len(newUser) > 0 ):
            if u in responses:
                newUsers.append((newUser[0].username, newUser[0].email))
                response = responses[u]
                response = sorted(response, key = lambda x: x[1], reverse= False)
                newResponse = [[response[0][1]]]        
                for i in range(0, len(response)):
                    if(response[i][0] == 'identify'):
                        newResponse.append([response[i][0], response[i][1].strftime("%Y-%m-%d %H:%M:%S"), "", "" ,response[i][1]])
                    elif(response[i][0] == 'Submitted Grade' or response[i][0] == 'Submitted Grade and Moved to Next User'):
                        newResponse.append([response[i][0], response[i][1].strftime("%Y-%m-%d %H:%M:%S"), (response[i][1] - newResponse[-1][-1]).total_seconds(),"", response[i][1]])
                    else:
                        newResponse.append([response[i][0], response[i][1].strftime("%Y-%m-%d %H:%M:%S"), (response[i][1] - newResponse[-1][-1]).total_seconds(), response[i][2], newResponse[-1][-1]])

                responses[u] = newResponse[1:]
            else:
                newUsers.append((newUser[0].username, newUser[0].email))
        else:
            print u

        num_questions=  0
        avg_time_per_question=0
        num_students = 0
        num_old_response = 0
        num_new_response = 0
        if u in responses:
            for response in responses[u]:
                if response[0] == 'Submitted Grade' or response[0] == 'Submitted Grade and Moved to Next User':
                    num_questions += 1
                    avg_time_per_question += float(response[2])
                if response[0] == 'response':
                    if(response[3] == 'Existing'):
                        num_old_response += 1
                    elif(response[3] == 'New'):
                        num_new_response += 1

        avg_time_per_question /= max(num_questions, 1)
        statistics[u] = [num_questions, avg_time_per_question, num_students, num_old_response, num_new_response]
    user = {'editors' : newUsers, "responses": responses, "stats": statistics}

    edit_response_forms = []            
    return render_template('dashboard/pages/admin.html', user=user, title='Admin', edit_response_forms=edit_response_forms, deleteUser=deleteUser)



