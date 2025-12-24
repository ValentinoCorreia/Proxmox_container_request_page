from flask import Blueprint
from flask import request, current_app
from flask import redirect, render_template, flash, url_for

from flask_login import login_user, login_required, current_user

from models.user import User
from models.connection import db
from models.container import Container, ContainerRequestStatus, ContainerTemplate

from utils.conversions import convertCPUSpeedStrToLimit
from utils.proxmox.lxc_manager import getLXCContainerStatus, StopLXCContainer, StartLXCContainer

bp = Blueprint("user_containers", __name__)

@bp.route("/container/<id>/<action>", methods=["GET", "POST"])
@login_required
def container(id: int, action = "show"):
    container_id = int(id)
    container = db.session.query(Container).filter_by(
        user_id=current_user.id,
        id =container_id,
        container_status=ContainerRequestStatus.approved
    ).one_or_none()

    if (container):
        if (action == "stop" and request.method == "POST"):
            print("stopped:", StopLXCContainer(container.lxc_proxmox_id))
        elif (action == "start" and request.method == "POST"):
            print("started:", StartLXCContainer(container.lxc_proxmox_id))
        lxc_full_status_info = getLXCContainerStatus(container.lxc_proxmox_id)
        return render_template("user/manage_container.html",
            container= container,
            lxc_container_status=lxc_full_status_info["status"],
            lxc_container_uptime=lxc_full_status_info["uptime"]
        )
    else:
        return "Unauthorized", 403

@bp.get("/containers")
def manageContainers():
    containers = db.session.query(Container).filter_by(
        user_id=current_user.id
    ).all()
    return render_template(
        "user/manage_containers.html",
        containers=containers,
        container_approved=ContainerRequestStatus.approved
    )

@bp.route("/container/add", methods=["GET", "POST"])
@login_required
def addContainer():
    if request.method == "GET":
        templates = db.session.query(ContainerTemplate).all()
        return render_template("user/request_container/request_form.html", os_templates=templates)
    else:
        password = request.form.get("container_root_password", "")
        password_repeat = request.form.get("container_root_repeat_password", "")

        if (len(password) == 0):
            flash("Root password is not optional")
            return redirect(url_for("user_containers.addContainer"))
        elif (len(password) < 5):
            flash("Root password must be at least 6 characters long")
            return redirect(url_for("user_containers.addContainer"))
        if (password != password_repeat):
            flash("Repeat password input is different")
            return redirect(url_for("user_containers.addContainer"))
        
        name = request.form.get("container_name", "").strip()
        if (len(name) == 0):
            flash("Container name is not optional")
            return redirect(url_for("user_containers.addContainer"))
        elif (len(name) >= 80):
            flash("Container name is too long")
            return redirect(url_for("user_containers.addContainer"))


        ram = request.form.get("container_ram")
        os = request.form.get("container_os")
        cpu_speed = request.form.get("container_cpu")
        if (ram == None or os == None or cpu_speed == None):
            flash("Please compile all parameters")
            return redirect(url_for("user_containers.addContainer"))
        ram = int(ram)
        if (
            ram < 256
            or ram > 4096
            or not db.session.query(ContainerTemplate).filter_by(name=os).one_or_none()
        ):
            return "Invalid parameter", 404
        
        container = Container()
        container.name = name
        container.cpu_limit = convertCPUSpeedStrToLimit(cpu_speed)
        container.ram = ram
        container.template_name = os
        container.initial_root_password = password
        container.container_status = ContainerRequestStatus.requested
        container.user_id = current_user.id
        db.session.add(container)
        db.session.commit()
        return render_template("user/request_container/success.html")