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

### Blueprint Templates ###

from ranker.views import dashboard
app.config.from_object('config')
app.register_blueprint(dashboard.dashboard)

### Logging ###

handler = RotatingFileHandler('info.log', maxBytes=10000, backupCount=1)
formatter = logging.Formatter(
            "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
app.logger.addHandler(handler)

