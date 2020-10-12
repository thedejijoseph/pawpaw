
import os

import flask
from flask import Flask, render_template
from flask_restplus import Api, Resource
import requests

import google_auth_oauthlib
import google.oauth2
import googleapiclient.discovery

from dotenv import load_dotenv
load_dotenv()

CLIENT_SECRETS_FILE = "env/client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile']
API_SERVICE_NAME = 'people'
API_VERSION = 'v1'

app = Flask(__name__)
app.secret_key = os.getenv('G_API_SECRET')

@app.route('/')
def root_view():
    return render_template('index.html')

api = Api(app, doc=False)

@api.route('/profile')
class Profile(Resource):
    def get(self):
        if 'credentials' not in flask.session:
            return flask.redirect(api.url_for(GetAuthorization))
        
        credentials = google.oauth2.credentials.Credentials(
            **flask.session['credentials']
        )
        people_service = googleapiclient.discovery.build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=credentials
        )
        profile = people_service.people().get(
            resourceName='people/me', personFields='names,emailAddresses'
        ).execute()
        name = profile['names'][0]['displayName']
        flask.session['credentials'] = credentials_to_dict(credentials)

        # return flask.jsonify(**profile)
        # return (f'Pawpaw profile for {name}. <a href="/revoke">Logout..</a>')
        return {'name': name, 'revoke_url': '/revoke'}
    
@api.route('/authorize')
class GetAuthorization(Resource):
    def get(self):
        # creating OAuth Flow
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES
        )
        flow.redirect_uri = api.url_for(OAuthCallback, _external=True)
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            inlucde_granted_scopes='true'
        )

        flask.session['state'] = state
        return flask.redirect(authorization_url)

@api.route('/oauth2callback')
class OAuthCallback(Resource):
    def get(self):
        state = flask.session['state']

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            state=state
        )
        flow.redirect_uri = api.url_for(OAuthCallback, _external=True)
        
        authorization_response = flask.request.url
        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials
        flask.session['credentials'] = credentials_to_dict(credentials)

        return flask.redirect(api.url_for(Profile))

@api.route('/revoke')
class Revoke(Resource):    
    def get(self):
        if 'credentials' not in flask.session:
            return ('OAuth unavailable. Authorize first: <a href="/authorize">authorize</a>.')
        
        credentials = google.oauth2.credentials.Credentials(
            **flask.session['credentials']
        )

        revoke = requests.post(
            'https://oauth2.googleapis.com/revoke',
            params={'token': credentials.token},
            headers={'content-type': 'application/x-www-form-urlencoded'}
        )
        if revoke.status_code == 200:
            # also clear credentials on the way out..
            ClearCredentials().get()
            # return ('Credentials successfully revoked. <a href="/">Go home</a>')
            return {'msg': 'Credentials successfully revoked.', 'next_url': '/'}
        else:
            # return ('An error occured.')
            return {'msg': 'An error occured.'}

@api.route('/clear')
class ClearCredentials(Resource):
    def get(self):
        if 'credentials' in flask.session:
            del flask.session['credentials']
        # return ('Credentials have been cleared. <a href="/">Go home</a>')
        return {'msg': 'Credentials have been cleared.', 'next_url': '/'}


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

if __name__ == "__main__":
    debug = True if os.getenv('DEBUG_APP') == 'True' else False
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('localhost', 8080, debug=debug)

