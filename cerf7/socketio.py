from dataclasses import asdict

from flask import current_app, g, session
from flask_socketio import SocketIO, emit, send, disconnect
from cerf7.db import User, ConversationMessage, DialogMessage


socketio = SocketIO()


@socketio.on("message")
def handle_message(data):
    current_app.logger.debug("Got message from WebSocket: " + data)


@socketio.on("connect")
def handle_connection():
    if "user_id" not in session:
        disconnect()

    g.user = User.query.get(session["user_id"])
    send(f"Greetings! Your passphrase is {g.user.passphrase}")


def send_available_message(main_character_message: ConversationMessage):
    emit("available-message", asdict(main_character_message))


def send_npc_message(npc_message: DialogMessage):
    emit("npc-message", asdict(npc_message))


def init_app(app):
    socketio.init_app(app)
