""" Class to preprocess and create grading response ranking models """

import itertools

import sys
sys.path.append('../../chat')

from ranking.skipthoughts import skipthoughts
from ranking.skipthoughts import eval_rank
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cross_validation import train_test_split
from sklearn.naive_bayes import MultinomialNB

from flask import Flask
from flask.ext.pymongo import PyMongo
import pickle
import sys
sys.path.insert(0, '../')
sys.path.insert(0, '../src')
from src import config
import chat_module
from sklearn.linear_model import LogisticRegression, SGDClassifier
#from chat_generator import ChatGenerator
import tokenize
import StringIO
import logging
from logging.handlers import RotatingFileHandler
import ast
import re
from sklearn import svm
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer


def findData():
    app = Flask(__name__)
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
    app.config['CELERY_BACKEND'] = 'redis://localhost:6379'

    ### Database ###
    app.config['MONGO2_URI'] = config.MONGO_URI + "grading-db"
    grading_db = PyMongo(app, config_prefix='MONGO2')

    with app.app_context():
        submissions = list(grading_db.db['submissions'].find({'answers': {'$not': {'$size': 0}}}).sort("_id", -1))
        num_questions = len(submissions[0]['grades'])
        data = []
        targets = []
        for i in range(num_questions):
            data.append([])
            targets.append([])
        print len(data), len(targets)
        count = [0,0,0,0,0]
        ncount = [0,0,0,0,0]
        sampleCode = []
        for i in range(5):
            f=open("questions/"+str(i)+".txt")
            sampleCode.append([])
            for line in f.readlines():
                sampleCode[i].append(line.strip())
        for idx, submission in enumerate(submissions):
            grades = submission['grades']
            answers = submission['answers']
            for i in range(len(answers)):
                result = grades[i]['result']
                code = answers[i]
                if len(code) > 0:
                    code = code[0]['source']
                    if sampleCode[i][0] == 'code':
                        for line in code:
                            #print line
                            try:
                                if(line.strip() not in sampleCode[i]):
                                    tokens = ""
                                    for token in tokenize.generate_tokens(StringIO.StringIO(line).readline):
                                        if(len(token[1]) > 0):
                                            #tokens.append(token[1])
                                            tokens += token[1] + " "

                                    tokens = tokens[:-1]
                                    #astCode = ast.dump(ast.parse(line))
                                    if(result == 'passed'):
                                        data[i].append(tokens)
                                        targets[i].append(1)
                                        count[i] += 1
                                    elif(result == 'failed'):
                                        for j in range((count[i] - ncount[i])):
                                        #for j in range(3):
                                            
                                            data[i].append(tokens)
                                            targets[i].append(0)
                                            ncount[i] +=1  
                            except:
                                #print("Couldn't tokenize: ", line)
                                pass
                    elif sampleCode[i][0] == 'text':
                        lines = ""
                        for line in code:
                            try:
                                if(line.strip() not in sampleCode[i]):
                                    for token in tokenize.generate_tokens(StringIO.StringIO(line).readline):
                                        if(len(token[1]) > 0):
                                            #tokens.append(token[1])
                                            lines += token[1] + " "
                            except:
                                pass

                        lines = lines[:-1]
                        lines = lines.split(' . ')
                        lines = [x for x in lines if len(x) > 1]
                        
                        #astCode = ast.dump(ast.parse(line))
                        if(result == 'passed'):
                            data[i] += lines
                            targets[i] += [1]*len(lines)
                            count[i] += 1
                        elif(result == 'failed'):
                            #for j in range(3):
                            for j in range((count[i] - ncount[i])):
                                data[i] += lines
                                targets[i] += [0]*len(lines)
                                ncount[i] +=1 

                                            
                    
        print count, ncount
        return (data, targets, sampleCode)


data, targets, sampleCode= findData()

for i in range(len(targets)):
    target = targets[i]
    print "Question ", i, float(sum(target))/len(target)


models = []

for i in range(len(data)):
    datum = data[i]
    answerType = sampleCode[i][0]
    print answerType
    if(answerType == 'code'):
        vectorizer = CountVectorizer(min_df=1, analyzer='word', token_pattern=u"(?u)\\b([^\\s]+)\\b")
        x = vectorizer.fit_transform(datum)
        tf_transformer = TfidfTransformer(use_idf=False).fit(x)
        x = tf_transformer.transform(x)
        model = svm.SVC(probability=True)
        #model = MultinomialNB()
    elif(answerType == 'text'):
        vectorizer = CountVectorizer(min_df=1, analyzer='word')
        x = vectorizer.fit_transform(datum)
        tf_transformer = TfidfTransformer(use_idf=False).fit(x)
        x = tf_transformer.transform(x)
        model = MultinomialNB()
        #model = svm.SVC(probability=True)
    model.fit(x, targets[i])
    print(model.score(x, targets[i]))
    models.append((model, vectorizer, tf_transformer))
pickle.dump(models, open("models.pkl", 'wb'))