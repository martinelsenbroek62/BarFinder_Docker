# cython: language_level=3
from datetime import datetime

import pytz
import click
from flask.cli import AppGroup
from flask import current_app as app

User = app.models.User


@app.cli.command(cls=AppGroup)
def users():
    """Perform user-related operations."""
    pass


@users.command()
@click.option('--email', type=str, prompt=True)
@click.option('--password', type=str, prompt=True,
              hide_input=True, confirmation_prompt=True)
@click.option('--is-admin', is_flag=True, prompt=True)
def create(email, password, is_admin):
    """Create a new user."""
    if '@' not in email:
        # just perform a simple test
        raise click.UsageError('Invalid email address "{}"'
                               .format(email))
    known_user = User.query.filter_by(email=email).one_or_none()
    if known_user:
        raise click.UsageError('User already existed "{}"'
                               .format(known_user.email))
    user = User(email=email, password=password, is_admin=is_admin,
                created_at=datetime.now(pytz.utc))
    app.db.session.add(user)
    app.db.session.commit()
    click.echo('User created "{}".'.format(user.email))


@users.command()
@click.option('--email', type=str, prompt=True)
@click.option('--password', type=str, prompt=True,
              hide_input=True, confirmation_prompt=True)
def change_password(email, password):
    """Change the password of an existing user."""
    user = User.query.filter_by(email=email).one_or_none()
    if not user:
        raise click.UsageError('User not found "{}"'
                               .format(email))
    user.password = password
    app.db.session.commit()
    click.echo('User password changed "{}".'.format(user.email))
