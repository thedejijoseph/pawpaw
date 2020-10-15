
import os
import string, random

POSTGRES_DB_URI = os.getenv('PG_DB_URI')

BASEDIR = os.path.abspath(os.path.dirname(__file__))

def generate_secret_key():
    pool = string.ascii_letters + string.digits
    return ''.join(random.choices(pool, k=64))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', generate_secret_key())
    DEBUG = False

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = POSTGRES_DB_URI
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = POSTGRES_DB_URI
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = POSTGRES_DB_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

key = Config.SECRET_KEY
