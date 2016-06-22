from flask import Flask
from flask.ext.pymongo import PyMongo

import sys
sys.path.insert(0, '../')
sys.path.insert(0, '../src')
from src import config
from chat_generator import ChatGenerator

import logging
from logging.handlers import RotatingFileHandler


### Chat Generation ###
cg = ChatGenerator(corpus_path='../src/corpus.pkl')

app = Flask(__name__)

### Database ###

app.config['MONGO_URI'] = config.MONGO_URI + config.MONGO_DB
mongo = PyMongo(app, config_prefix='MONGO')

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

