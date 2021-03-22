# cython: language_level=3

import pytz
import json
import click
from datetime import datetime, timedelta

from flask_mail import Message
from flask import current_app as app


@app.cli.command()
@click.argument('sender', type=str)
@click.argument('recipient', type=str)
def mail_usage_stat(sender, recipient):
    User = app.models.User
    UsageLog = app.models.UsageLog

    now = datetime.now(pytz.utc)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    weekago = midnight - timedelta(days=7)
    one_day = timedelta(days=1)

    query = (User.query
             .filter(User.usage_logs.any(UsageLog.created_at >= weekago)))
    results = []
    for user in query:
        usage_logs = [l for l in user.usage_logs if l.created_at >= weekago]
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
            'amount_in_7_days': duration_by_week,
            'amount_by_day': duration_by_day
        })
    msg = Message('Usage Stat',
                  sender=sender,
                  recipients=[recipient])
    msg.body = json.dumps(results)
    app.mail.send(msg)
