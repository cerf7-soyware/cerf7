from flask import current_app, session
from flask_socketio import SocketIO, emit, send
from cerf7.db import db, User


socketio = SocketIO()


@socketio.on("message")
def handle_message(data):
    current_app.logger.debug("Got message from WebSocket: " + data)


@socketio.on("connect")
def handle_connection():
    user_id = session["userId"]
    user_passphrase = User.query.get(user_id).passphrase

    send(f"Greetings! Your passphrase is {user_passphrase}")


def notify_about_available_conversation():
    send("A new conversation is available!")


def init_app(app):
    socketio.init_app(app)
