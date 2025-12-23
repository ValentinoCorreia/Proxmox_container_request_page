from models.connection import db
from models.user import User

import click

from app import app

@app.cli.command("create_user")
@click.option('--username', prompt='Username', required=True)
@click.option('--password', prompt='User password', required=True)
@click.option('--is-admin', required=False, is_flag=True)
def create_user(username, password, is_admin):
    from models.user import User

    user = db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar_one_or_none()
    if (user == None):
        new_user = User()
        new_user.username = username
        new_user.set_password(password)
        new_user.is_admin = is_admin

        db.session.add(new_user)
        db.session.commit()
    else:
        print("User already exist")

@app.cli.command("delete_user")
@click.option('--username', prompt='Username', required=True)
def delete_user(username):
    user = db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar_one_or_none()
    if (user != None):
        db.session.delete(user)
        db.session.commit()
    else:
        print("User don't exist")