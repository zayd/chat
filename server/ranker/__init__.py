from flask import Flask, request, render_template, redirect, url_for
from flask.ext.pymongo import PyMongo
from flask.ext.login import LoginManager, UserMixin, login_required, login_user
from flask.ext.sqlalchemy import SQLAlchemy  
from datetime import datetime

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
    
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)



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

class User(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id',db.Integer , primary_key=True)
    username = db.Column('username', db.String(20), unique=True , index=True)
    password = db.Column('password' , db.String(10))
    email = db.Column('email',db.String(50),unique=True , index=True)
    registered_on = db.Column('registered_on' , db.DateTime)
 
    def __init__(self , username ,password , email):
        self.username = username
        self.password = password
        self.email = email
        self.registered_on = datetime.utcnow()
 
    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return unicode(self.id)
 
    def __repr__(self):
        return '<User %r>' % (self.username)


def createUser(username, password, email):
    return User(username, password, email)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    user = User(request.form['username'] , request.form['password'],request.form['email'])
    db.session.add(user)
    db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']
    registered_user = User.query.filter_by(username=username,password=password).first()
    if registered_user is None:
        flash('Username or Password is invalid' , 'error')
        return redirect(url_for('login'))
    login_user(registered_user)
    #flash('Logged in successfully')
    return redirect(request.args.get('next') or url_for('index'))