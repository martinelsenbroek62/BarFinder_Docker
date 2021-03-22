# cython: language_level=3

import pytz
from datetime import datetime, timedelta

from flask_restful import Resource
from flask import current_app as app
from werkzeug.exceptions import Unauthorized
from flask_jwt_extended import jwt_required, get_jwt_identity


class UsageStatAPI(Resource):
    decorators = [jwt_required]

    def post(self):
        User = app.models.User
        UsageLog = app.models.UsageLog

        email = get_jwt_identity()
        current_user = User.get_by_email(email)
        if not current_user.is_admin:
            raise Unauthorized('Current account is not authorized '
                               'to access this endpoint.')

        now = datetime.now(pytz.utc)
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        weekago = midnight - timedelta(days=7)
        one_day = timedelta(days=1)

        query = (User.query
                 .filter(User.usage_logs.any(UsageLog.created_at >= weekago)))
        results = []
        for user in query:
            usage_logs = [l for l in user.usage_logs
                          if l.created_at >= weekago]
            duration_by_week = sum(l.instance_quantity for l in usage_logs)
            duration_by_day = []
            for dayoffset in range(7):
                date = weekago + timedelta(days=dayoffset)
                duration_by_day.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'duration': sum(l.instance_quantity for l in usage_logs
                                    if l.created_at >= date and
                                    l.created_at < date + one_day)
                })
            results.append({
                'user_id': user.id,
                'user_email': user.email,
                'report_time': now.isoformat(),
                'amount_in_last_week': duration_by_week,
                'amount_by_day': duration_by_day
            })
        return results
