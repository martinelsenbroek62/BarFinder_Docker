# cython: language_level=3
"""Provide init_app function"""
import logging
from flask import Flask
from celery import Celery

from flask_login import LoginManager
from flask_jwt_extended import JWTManager

from .apis import init_api
from .socketio_apis import init_socketio_api


def init_celery(app):
    """Initialize Celery instance"""
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.result_expires = app.config['CELERY_TASK_RESULT_EXPIRES']

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def init_db(app):
    """Initialize SQLAlchemy"""
    from flask_sqlalchemy import SQLAlchemy
    from flask_alembic import Alembic

    db = SQLAlchemy(app)
    Alembic(app)
    return db


def init_mail(app):
    from flask_mail import Mail
    return Mail(app)


def load_models(app):
    from . import models
    return models


def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return app.models.User.query.get(user_id)

    return login_manager


def init_jwt_manager(app):
    jwt_manager = JWTManager(app)
    return jwt_manager


def load_custom_commands(app):
    from . import commands
    return commands


def init_cors(app):
    from flask_cors import CORS
    CORS(app,
         supports_credentials=True,
         resources={
             r"/*": {"origins": app.config['ALLOWED_ORIGIN']}
         })
    return app


def init_logger(app):
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)


def init_app():
    """Initialize Flask application"""
    app = Flask(__name__.rsplit('.', 1)[0])

    with app.app_context():
        # load config
        app.config.from_object('api_collection.config.Default')

        init_logger(app)

        # load db
        app.db = init_db(app)

        # load flask-mail
        app.mail = init_mail(app)

        # load models
        app.models = load_models(app)

        # init_cors
        init_cors(app)

        # load login_manager
        # init_login_manager(app)

        # load jwt_manager
        init_jwt_manager(app)

        # load custom commands
        load_custom_commands(app)

        # load celery
        app.celery = init_celery(app)

        # load APIs
        app.api = init_api(app)

        # load SocketIO APIs
        init_socketio_api(app)

    return app
