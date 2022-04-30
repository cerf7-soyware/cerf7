import json

from dataclasses import asdict
from functools import wraps
from flask import current_app, g, session, request
from flask_socketio import SocketIO, send, disconnect
from cerf7.db import User, ConversationMessage, DialogMessage


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
    current_app.logger.debug("New SocketIO connection")
    send(f"Greetings! Your passphrase is {g.user.passphrase}")


@socketio.on("disconnect")
def handle_disconnection():
    current_app.logger.debug("SocketIO disconnection")


@socketio.on("user-message")
@authenticated_only
def handle_user_message(message_params):
    current_app.logger.debug("Handling user message")
    raise NotImplementedError()


def send_available_message(
        whom: User, main_character_message: ConversationMessage):
    socketio.emit(
        "available-message",
        json.dumps(asdict(main_character_message), ensure_ascii=False),
        room=whom.current_sid)


def send_npc_message(whom: User, npc_message: DialogMessage):
    socketio.emit(
        "npc-message",
        json.dumps(asdict(npc_message), ensure_ascii=False),
        room=whom.current_sid)


def send_offline(whom: User):
    socketio.emit("main-character-offline", room=whom.current_sid)


def send_back_online(whom: User):
    socketio.emit("main-character-back-online", "{}", room=whom.current_sid)


def send_time_travel(whom: User):
    socketio.emit(
        "time-travel", str(whom.in_game_state.datetime),
        room=whom.current_sid)


def init_app(app):
    socketio.init_app(app)
