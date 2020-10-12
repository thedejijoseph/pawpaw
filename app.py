
import os

import flask
from flask import Flask, render_template
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

@app.route('/profile')
def profile():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('get_authorization'))
    
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
    return (f'Pawpaw profile for {name}. <a href="/revoke">Logout..</a>')
    
@app.route('/authorize')
def get_authorization():
    # creating OAuth Flow
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES
    )
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        inlucde_granted_scopes='true'
    )

    flask.session['state'] = state
    return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect(flask.url_for('profile'))

@app.route('/revoke')
def revoke_oauth():
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
        clear_credentials()
        return ('Credentials successfully revoked. <a href="/">Go home</a>')
    else:
        return ('An error occured.')

@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return ('Credentials have been cleared. <a href="/">Go home</a>')


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

