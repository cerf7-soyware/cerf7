from functools import wraps
from flask import current_app, g, session
from flask_socketio import SocketIO, emit, send, disconnect
from cerf7.db import db, User


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


def notify_about_available_conversation():
    send("A new conversation is available!")


def init_app(app):
    socketio.init_app(app)
