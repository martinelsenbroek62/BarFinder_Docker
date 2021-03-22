# cython: language_level=3
from flask import current_app as app
from sqlalchemy_utils import EmailType, PasswordType

db = app.db


class User(db.Model):
    __tablename__ = 'tbl_users'

    id = db.Column(
        db.Integer, primary_key=True, nullable=False,
        doc='user unique identifier')
    email = db.Column(
        EmailType, unique=True, nullable=False,
        doc='user email; used as login name')
    password = db.Column(
        PasswordType(schemes=['pbkdf2_sha512']),
        nullable=False, doc='user password (hashed)')
    is_admin = db.Column(
        db.Boolean, nullable=False, doc='is this user an admin')
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, index=True,
        doc='date and time this user was created')

    usage_logs = db.relationship('UsageLog', backref='user')

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).one_or_none()

    @property
    def is_active(self):
        # check https://flask-login.readthedocs.io/en/latest/#your-user-class
        # for implementation detail. Currently not implemented.
        return True

    @property
    def is_authenticated(self):
        # check https://flask-login.readthedocs.io/en/latest/#your-user-class
        # for implementation detail. Currently not implemented.
        return True

    @property
    def is_anonymous(self):
        # check https://flask-login.readthedocs.io/en/latest/#your-user-class
        # for implementation detail. Currently not implemented.
        return False

    def get_id(self):
        return str(self.id)

    def log_usage(self, instance_name, instance_quantity):
        log = app.models.UsageLog(self, instance_name, instance_quantity)
        self.usage_logs.append(log)
        return log
