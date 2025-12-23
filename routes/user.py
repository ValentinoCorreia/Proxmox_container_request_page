from flask import Blueprint
from flask import request, current_app
from flask import redirect, render_template, flash, url_for

from flask_login import login_user

from models.user import User
from models.connection import db

bp = Blueprint("user", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if (username == "" or password == "" ):
            flash("Invalid data")
            return redirect(url_for("user.login"))
        else:
            user = db.session.execute(
                db.select(User).filter_by(username=username)
            ).scalar_one_or_none()

            if (user):
                if (user.password_check(password)):
                    login_user(user)
                    return redirect(url_for("index"))

        flash("Invalid login")
        return redirect(url_for("user.login"))