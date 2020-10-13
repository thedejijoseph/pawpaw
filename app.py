
import os

import flask
from flask import Flask
from flask_restplus import Api, Resource, reqparse
import requests

from google.oauth2 import id_token
from google.auth.transport import requests

import sqlalchemy

from dotenv import load_dotenv
load_dotenv()

from services import *

CLIENT_ID = os.getenv('G_API_CLIENT_ID')

app = Flask(__name__)
app.secret_key = os.getenv('G_API_SECRET')
api = Api(app, doc=False)

@api.route('/')
class RootView(Resource):
    def get():
        return {'msg': 'You are at root'}


@api.route('/token-signup')
class TokenSignup(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('idtoken', required=True, help='IDToken must be specified.')
        args = parser.parse_args()
        token = args['idtoken']

        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
            if not user_exists(idinfo['email']):
                app_token = create_user(idinfo['name'], idinfo['email'], idinfo['jti'])
                return {'msg': 'User created successfully.', 'token': app_token}
            else:
                return {'error': 'User exists already'}
        except ValueError:
            return {'error': 'Could not verify token.'}, 400
        except sqlalchemy.exc.IntegrityError:
            return {'error': 'User exists already'}


@api.route('/token-signin')
class TokenSignin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('idtoken', required=True, help='IDToken must be specified.')
        args = parser.parse_args()
        token = args['idtoken']

        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
            app_token = token_signin_get_token(idinfo['email'])
            return {'msg': 'User authenticated successfully.', 'token': app_token}
        except ValueError:
            return {'error': 'Could not verify token.'}, 400

@api.route('/profile')
class Profile(Resource):
    """Profile Endpoint fetches profile info related to the signed in account.
    """

    def post(self):
        auth_header = flask.request.headers.get('Authorization')
        user = authenticate_user(auth_header)
        flask.session['user'] = user.email
        return {'name': user.name, 'email': user.email}


if __name__ == "__main__":
    debug = True if os.getenv('DEBUG_APP') == 'True' else False
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('localhost', 8081, debug=debug)

