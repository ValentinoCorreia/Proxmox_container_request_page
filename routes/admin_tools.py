from flask import Blueprint
from flask import request, current_app
from flask import redirect, render_template, flash, url_for

from flask_login import login_user, login_required, current_user

from models.user import User
from models.container import Container, ContainerRequestStatus, ContainerTemplate
from models.connection import db

from utils.proxmox.lxc_manager import createLXCContainer


bp = Blueprint("admin_tools", __name__)

@bp.before_request
@login_required
def check_is_admin():
    if (not current_user.is_admin):
        return "Access deny", 403

# templates

@bp.route("templates", methods=["GET", "POST"])
def manage_templates():
    if (request.method == "POST"):
        display_name = request.form.get("name").strip()
        proxmox_name = request.form.get("proxmox_name").strip()

        if (display_name or proxmox_name):
            template = ContainerTemplate()
            template.name = display_name
            template.proxmox_os_template = proxmox_name
            db.session.add(template)
            db.session.commit()
        else:
            flash("Invalid params")
    return render_template(
        "admin_tools/manage_templates.html",
        page="templates",
        templates=db.session.query(ContainerTemplate).all()
    )

@bp.post("template/<name>/remove")
def template_remove(name):
    
    template = db.session.query(ContainerTemplate).filter_by(name=name).one_or_none()

    db.session.delete(template)
    db.session.commit()

    return redirect(url_for("admin_tools.manage_templates"))

# containers

@bp.route("containers")
def containers():
    return redirect(url_for("admin_tools.pending_containers"))

@bp.route("containers/pending")
def pending_containers():
    containers = db.session.query(Container).filter_by(
        container_status=ContainerRequestStatus.requested
        ).all()
    
    return render_template("admin_tools/pending_containers.html", containers=containers, page="requests")


@bp.post("container/<id>/<action>")
def container_request_action(id, action):
    try:
        converted_id = int(id)
    except:
        return {"message": f"'{id}' is not a valid id"}, 400
    
    container = db.session.query(Container).filter_by(id=converted_id).one_or_none()
    if (container):
        if (action == "accept"):
            container.lxc_proxmox_id = createLXCContainer(container)
            container.container_status = ContainerRequestStatus.approved
        elif (action == "refuse"):
            container.container_status = ContainerRequestStatus.refused
        db.session.merge(container)
        db.session.commit()
    else:
        print("action skipped container is null")

    return redirect(url_for("admin_tools.pending_containers"))