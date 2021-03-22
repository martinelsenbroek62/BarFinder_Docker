# cython: language_level=3
from flask import session
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_jwt_extended.exceptions import (NoAuthorizationError,
                                           InvalidHeaderError)
from flask_socketio import disconnect, emit


def init_socketio_api(app):
    """Initialize SocketIO APIs"""
    from flask_socketio import SocketIO
    app.socketio = SocketIO(
        app,
        cors_allowed_origins=app.config['ALLOWED_ORIGIN'])

    @app.socketio.on('connect')
    def connect_handler():
        try:
            verify_jwt_in_request()
        except (NoAuthorizationError, InvalidHeaderError):
            emit('error', {
                'event': 'connect',
                'status': 'error',
                'error_message': 'Invalid or not provided access token.'
            })
            disconnect()
        session['current_user_email'] = get_jwt_identity()

    from .livestream import livestream  # noqa
