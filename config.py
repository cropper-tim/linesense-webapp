import os
import psycopg2

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'line-sense-secret-key'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgres://xlrygunwhhtirx:c29f595badd037c70422a8f8e1e98c11281fc686883fff6558de29a22d4846ab@ec2-54-225-121-235.compute-1.amazonaws.com:5432/d7i79n09m3b404'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
