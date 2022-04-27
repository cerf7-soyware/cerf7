import datetime
import json

from dataclasses import asdict
from functools import wraps
from flask import current_app, g, session, request
from flask_socketio import SocketIO, send, disconnect
import cerf7.storyline as storyline
from cerf7.db import (
    db, User, Conversation, ConversationMessage, DialogMessage, AvailableMessage
)

socketio = SocketIO()


def authenticated_only(handler):
    @wraps(handler)
    def wrapped(*args, **kwargs):
        if "user" not in g:
            if "user_id" in session:
                g.user = User.query.get(session["user_id"])
            else:
                disconnect()

        return handler(*args, **kwargs)

    return wrapped


@socketio.on("message")
def handle_message(data):
    current_app.logger.debug("Got message from WebSocket: " + data)


@socketio.on("connect")
@authenticated_only
def handle_connection():
    g.user.current_sid = request.sid
    db.session.flush()

    print("New connection")

    send(f"Greetings! Your passphrase is {g.user.passphrase}")


@socketio.on("disconnect")
def handle_disconnection():
    print("Disconnect handled")


@socketio.on("user-message")
@authenticated_only
def handle_user_message(message_params):
    print("Handling user message")
    message_approved = AvailableMessage.query.get(
        (g.user.user_id, message_params["conversation_id"],
         message_params["from_state"], message_params["to_state"])) is not None
    if message_approved:
        conversation = Conversation.query.get(message_params["conversation_id"])
        conversation_handle = storyline.ConversationHandle(g.user, conversation)
        conversation_handle.follow_user_choice(
            message_params["from_state"], message_params["to_state"])


class DateTimeAwareJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.timestamp()

        return json.JSONEncoder.default(self, o)


def send_available_message(
        whom: User, main_character_message: ConversationMessage):
    socketio.emit(
        "available-message",
        json.dumps(
            asdict(main_character_message), cls=DateTimeAwareJSONEncoder,
            ensure_ascii=False),
        room=whom.current_sid)


def send_npc_message(whom: User, npc_message: DialogMessage):
    socketio.emit(
        "npc-message",
        json.dumps(
            asdict(npc_message), cls=DateTimeAwareJSONEncoder,
            ensure_ascii=False),
        room=whom.current_sid)


def send_message_expiration(whom: User, expired_message: AvailableMessage):
    socketio.emit(
        "expired-message",
        json.dumps(
            asdict(expired_message), cls=DateTimeAwareJSONEncoder,
            ensure_ascii=False),
        room=whom.current_sid)


def send_offline(whom: User):
    socketio.emit("main-character-offline", room=whom.current_sid)


def send_back_online(whom: User):
    socketio.emit("main-character-back-online", "{}", room=whom.current_sid)


def init_app(app):
    socketio.init_app(app)
