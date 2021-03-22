# cython: language_level=3
from datetime import datetime, timedelta

from flask import request
from flask import current_app as app
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from werkzeug.exceptions import BadRequest


class AccessTokenAPI(Resource):

    def post(self):
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        if not email:
            raise BadRequest('Missing email parameter.')
        if not password:
            raise BadRequest('Missing password parameter.')

        user = app.models.User.get_by_email(email)
        if not user or user.password != password:
            raise BadRequest('Wrong password or non-existing user.')
        expires = timedelta(days=1)
        access_token = create_access_token(
            identity=user.email, expires_delta=expires)
        return {
            'email': user.email,
            'is_admin': user.is_admin,
            'access_token': access_token,
            'expiration': (datetime.utcnow() + expires).isoformat() + 'Z'
        }
