# cython: language_level=3
"""Package apis"""
import json
from flask_restful import Api
from flask import Response
from werkzeug.exceptions import HTTPException


class ErrorsApi(Api):
    """Customize flask_restful.Api for handling errors"""

    def handle_error(self, err):
        """Customize error handler to output the exact error message"""
        if self.app.config.get('DEBUG'):
            return super(ErrorsApi, self).handle_error(err)
        err_name = type(err).__name__
        if err_name in ('ValidationError', 'ConnectionError',
                        'JSONDecodeError', 'FileNotFoundError',
                        'IsADirectoryError'):
            code = 400
        elif isinstance(err, HTTPException):
            code = err.code
        else:
            code = 500
        return Response(json.dumps({
            'error': err_name,
            'message': str(err)
        }), status=code, mimetype='application/json')


def init_api(app):
    """Initialize flask-restful instance"""
    api = ErrorsApi(app, catch_all_404s=True)

    from .access_token import AccessTokenAPI
    from .convert_audio import ConvertAudioAPI
    from .task_subscription import TaskSubscriptionAPI
    from .usage_stat import UsageStatAPI
    api.add_resource(AccessTokenAPI,
                     '/access_token',
                     endpoint='access_token')
    api.add_resource(ConvertAudioAPI,
                     '/convert_audio',
                     '/convert_audio/<string:task_id>',
                     endpoint='convert_audio')
    api.add_resource(TaskSubscriptionAPI,
                     '/task_subscription',
                     '/task_subscription/<string:bulk_task_id>',
                     endpoint='task_subscription')
    api.add_resource(UsageStatAPI,
                     '/usage_stat',
                     endpoint='usage_stat')
    return api
