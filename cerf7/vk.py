from flask import (
    Blueprint, g, redirect, url_for, request, session, current_app,
    render_template
)

from cerf7.auth import login_required


bp = Blueprint("vk", __name__)


@bp.route("/im")
@login_required
def messages():
    return render_template("vk/messages.html")
