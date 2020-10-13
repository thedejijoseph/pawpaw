
from models import session, User, Token


def create_token(name, email):
    pass

def retrieve_info(token):
    user_id = session.query(Token.user_id).filter(Token.key==token)[0]
    user = session.query(User).filter(User.id==user_id)[0]
    return user


def create_user(name, email, token):
    user = User(name=name, email=email)
    session.add(user)
    session.commit()

    # TODO: generate unique tokens for each user
    # temporary implementation
    token = Token(user_id=user.id, key=token)
    session.add(token)
    session.commit()
    return token.key

def user_exists(email):
    q = session.query(User).filter(User.email==email)
    if list(q):
        return True
    else:
        return False

def token_signin_get_token(email):
    user_id = session.query(User.id).filter(User.email==email)
    token = session.query(Token).filter(Token.user_id==user_id)[0]
    return token.key

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
