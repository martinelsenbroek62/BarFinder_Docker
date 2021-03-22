# cython: language_level=3
import uuid
from datetime import datetime

import pytz
from flask import current_app as app
from sqlalchemy_utils import UUIDType

db = app.db


class UsageLog(db.Model):
    __tablename__ = 'tbl_usage_logs'

    id = db.Column(
        UUIDType, primary_key=True, nullable=False,
        doc='usage log unique identifier')
    user_id = db.Column(
        db.Integer, db.ForeignKey('tbl_users.id'),
        index=True, nullable=False,
        doc='user id (foreign key)')
    instance_name = db.Column(
        db.Unicode(255), index=True, nullable=False,
        doc='used instance')
    instance_quantity = db.Column(
        db.Integer, index=True, nullable=False,
        doc='used instance quantity')
    created_at = db.Column(
        db.DateTime(timezone=True), index=True, nullable=False,
        doc='date and time this log was created')

    def __init__(self,
                 user, instance_name,
                 instance_quantity):
        self.id = uuid.uuid4()
        self.user = user
        self.instance_name = instance_name
        self.instance_quantity = instance_quantity
        self.created_at = datetime.now(pytz.utc)
