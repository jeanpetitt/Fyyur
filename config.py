import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

...
# Database initialization
if os.environ.get('DATABASE_URL') is None:
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:2002@localhost/fyyur'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

# TODO IMPLEMENT DATABASE URL
# SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:2002@localhost/fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False
