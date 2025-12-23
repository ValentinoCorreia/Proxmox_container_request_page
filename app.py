from os import getenv
from flask import Flask, redirect, url_for
from flask_login import LoginManager, login_required, current_user

from flask_migrate import Migrate

from models.connection import db
from models.user import User

from routes.user import bp as user_bp
from routes.admin_tools import bp as admin_tools_bp
from routes.user_containers import bp as user_containers_bp


app = Flask(__name__)
app.register_blueprint(user_bp)
app.register_blueprint(admin_tools_bp, url_prefix='/admin')
app.register_blueprint(user_containers_bp)

app.config['SQLALCHEMY_DATABASE_URI'] = getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///database.db")
if getenv("SECRET_KEY") == None:
    print("SECRET_KEY variable is not set.")
    exit()
else:
    app.config['SECRET_KEY'] = getenv("SECRET_KEY")

login_manager = LoginManager()
login_manager.login_view = "user.login";
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    return user


db.init_app(app)
migrate = Migrate(app, db)

@app.route("/")
@login_required
def index():
    if (current_user.is_admin):
        return redirect(url_for("admin_tools.containers"))
    else:
        return redirect(url_for("user_containers.manageContainers"))



#cli user management
import cli.user_manager



if __name__ == "__main__":
    app.run()