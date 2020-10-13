
from models import session, User, Token


def create_token(name, email):
    pass

def retrieve_info(token):
    return token

def create_user(name, email):
    user = User(name=name, email=email)
    session.add(user)
    session.commit()

    # TODO: generate unique tokens for each user
    return email

def authenticate(func):
    # TODO: retrieve user info from token
    def wrapper():
        print('waht')
        auth_header = flask.request.headers.get('Authorization')
        if not auth_header:
            return {'error': 'Invalid authentication'}  
        try:
            token = auth_header.split('Bearer ')[1]
            user = retrieve_info(token)
            flask.session['user'] = user
        except:
            raise
            # return {'error': 'Could not parse token'}
    return wrapper

def authenticate_user(auth_header):
    if not auth_header:
        return {'error': 'Invalid authentication'}  
    try:
        token = auth_header.split('Bearer ')[1]
        user = retrieve_info(token)
        return user
    except:
        raise


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}
