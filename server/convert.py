from flask import Flask
from flask.ext.pymongo import PyMongo
import tokenize
import StringIO
import sys
sys.path.insert(0, '../')
sys.path.insert(0, '../src')
from src import config
import chat_module
#from chat_generator import ChatGenerator
import pickle
import logging
import numpy as np
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
models = pickle.load(open("../src/models.pkl", "rb"))

### Blueprint Templates ###
with app.app_context():
    result = new_grading_db.db['submissions'].delete_many({})
    print(result.deleted_count)

    sampleCode = []
    for i in range(5):
            f=open("../src/questions/"+str(i)+".txt")
            sampleCode.append([])
            for line in f.readlines():
                sampleCode[i].append(line.strip())
    submissions = grading_db.db['submissions']
    newSubmissions = new_grading_db.db['submissions']
    for sub in (list(submissions.find())):
        sub = dict(sub)
        a = sub['answers']
        newAnswers = []
        for i in range(len(a)):
            model = models[i][0]
            vectorizer = models[i][1]
            tfidf = models[i][2]
            newAnswers.append([])
            for block in a[i]:
                newBlock = []
                for line in block['source']:
                    try:
                        #print line, len(line)
                        #print("Line:", line.strip())
                        if(line.strip() not in sampleCode[i]):
                            tokens = ""
                            for token in tokenize.generate_tokens(StringIO.StringIO(line).readline):
                                #tokens.append(token[1])
                                tokens += token[1] + " "
                            tokens = tokens[:-1]
                            
                            x = vectorizer.transform([tokens])
                            x = tfidf.transform(x)
                            y = model.predict(x)

                            #print(y)
                            
                            #print tokens
                            #print tokens, en(tokens)
                            
                            

                            result = model.predict_proba(x)
                            #print result.shape                        
                            prob = result[0,1]
                            #print result
                            #print prob
                            if prob > .9:
                                newBlock.append(['highlight-pass', line])
                            elif prob < .4:
                                newBlock.append(['highlight-fail', line])
                            else:
                                newBlock.append(['none', line])
                        else:
                            #print("Sample:", line)
                            newBlock.append(['none', line])
                    except:
                        #print("Couldn't tokenize: ", line)
                    #    print "hi"
                        newBlock.append(['none', line])
                newAnswers[-1].append({'source': newBlock})
        sub['answers']=newAnswers
        newSubmissions.insert_one(sub)


         