from flask import Flask
from flask.ext.pymongo import PyMongo

import sys
sys.path.insert(0, '../')
sys.path.insert(0, '../src')
from src import config
import chat_module
#from chat_generator import ChatGenerator

import logging
from logging.handlers import RotatingFileHandler

### Chat Generation ###
#cg = ChatGenerator(corpus_path='../src/corpus.pkl')

### App ###

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
app.config['CELERY_BACKEND'] = 'redis://localhost:6379'

### Database ###

app.config['MONGO_URI'] = config.MONGO_URI + config.MONGO_DB
chat_db = PyMongo(app, config_prefix='MONGO')
app.config['MONGO2_URI'] = config.MONGO_URI + "grading-db"
grading_db = PyMongo(app, config_prefix='MONGO2')
app.config['MONGO3_URI'] = config.MONGO_URI + "new-grading-db"
new_grading_db = PyMongo(app, config_prefix='MONGO3')


### Blueprint Templates ###
with app.app_context():
    result = new_grading_db.db['submissions'].delete_many({})
    print(result.deleted_count)

    submissions = grading_db.db['submissions']
    newSubmissions = new_grading_db.db['submissions']
    for sub in (list(submissions.find())):
        sub = dict(sub)
        a = sub['answers']
        newAnswers = []
        for x in a:
            newAnswers.append([])
            for block in x:
                newBlock = []
                for line in block['source']:
                    newBlock.append(['<div class=highlight-pass>{}</div>', line])
                newAnswers[-1].append({'source': newBlock})
        sub['answers']=newAnswers
        newSubmissions.insert_one(sub)


         