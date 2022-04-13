from os import environ


class DefaultConfig:
    # Flask environment
    FLASK_ENV = "development"
    TESTING = True
    SECRET_KEY = environ["SECRET_KEY"]

    # Database
    SQLALCHEMY_DATABASE_URI = environ["SQLALCHEMY_DATABASE_URI"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
