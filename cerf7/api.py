from flask import Blueprint, current_app
from cerf7.db import db


bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/get_user_chats", methods=["POST"])
def get_user_chats():
    pass


@bp.route("/load_chat_messages", methods=["POST"])
def load_chat_messages():
    pass
