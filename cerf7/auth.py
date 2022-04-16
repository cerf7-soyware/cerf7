import random

from functools import wraps
from sqlalchemy.exc import IntegrityError
from cerf7.english_words import english_words_lower_list
from cerf7.db import db, User
from cerf7.storyline import user_bootstrap
from flask import (
    Blueprint, g, session, request, redirect, url_for, abort, flash
)


bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["POST"])
def login():
    # Invalidate previous user session and login into another account

    user_passphrase = request.form["passphrase"]
    if user_passphrase is None:
        abort(400, "No authentication passphrase provided")

    user = User.query\
        .filter_by(passphrase=user_passphrase)\
        .first()
    if user is None:
        flash(f"User with passphrase '{user_passphrase}' not found")
    else:
        session.clear()
        session.permanent = True
        session["user_id"] = user.user_id
        flash(f"Logged in with passphrase '{user_passphrase}'")

    return redirect(url_for("vk.messages"))


@bp.route("/signup", methods=["GET"])
def signup():
    while True:
        try:
            # Try to generate a unique passphrase for new user and insert user
            # record in the DB. Passphrase collision is unlikely to happen,
            # success in the first iteration is expected.

            words_in_passphrase = 4
            user_passphrase = " ".join(random.choices(
                english_words_lower_list, k=words_in_passphrase))

            g.user = User(passphrase=user_passphrase)
            db.session.add(g.user)
            db.session.commit()

            session.clear()
            session.permanent = True
            session["user_id"] = g.user.user_id

            user_bootstrap()

            return redirect(url_for("vk.messages"))
        except IntegrityError:
            db.session.rollback()


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is not None:
        g.user = User.query.get(user_id)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.signup"))

        return view(*args, **kwargs)

    return wrapped_view
