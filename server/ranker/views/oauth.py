import sys
sys.path.insert(0, '../../')
from src import config

import flask
from flask import request, session
from ranker import app
from ranker import mongo
#from parakeet import db
#from parakeet.models import Credentials, Example, Response
from requests_oauthlib import OAuth2Session

import json
import base64
import httplib2


@app.route('/success')
def success():
  return 'Success!'

@app.route('/authorize')
def authorize():
  SCOPES = ["read"]

  if 'code' not in flask.request.args:
    oauth = OAuth2Session(config.ZOPIM_CLIENT_ID,
              redirect_uri=config.ZOPIM_REDIRECT_URI, scope=SCOPES)
    auth_uri, state = oauth.authorization_url(config.ZOPIM_AUTH_URI)
    session['oauth_state'] = state
    session['username'] = flask.request.args.get('username', 'None')
    print auth_uri
    return flask.redirect(auth_uri)
  else:
    #auth_code = flask.request.args.get('code')
    oauth = OAuth2Session(config.ZOPIM_CLIENT_ID, state=session['oauth_state'],
              scope=SCOPES, redirect_uri=config.ZOPIM_REDIRECT_URI)

    token = oauth.fetch_token(config.ZOPIM_TOKEN_URI, client_id=config.ZOPIM_CLIENT_ID,
        authorization_response=request.url, client_secret=config.ZOPIM_CLIENT_SECRET,
        scope=SCOPES)
      #,
      #grant_type="authorization_code")

    token['username'] = session['username']
    mongo.db['tokens'].insert(token)

    #else:
    #  user.credentials = credentials.to_json()

    #db.session.commit()

    #flask.session['credentials'] = credentials.to_json()
    return flask.redirect(flask.url_for('success'))
