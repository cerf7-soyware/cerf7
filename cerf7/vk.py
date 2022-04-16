from flask import (
    Blueprint, g, redirect, url_for, request, session, current_app,
    render_template
)

from cerf7.auth import login_required
from cerf7.db import db, User


bp = Blueprint("vk", __name__)


@bp.route("/im")
@login_required
def messages():
    user_passphrase = User.query.get(session["user_id"]).passphrase
    return render_template("vk/messages.html", user_passphrase=user_passphrase)
