from flask import current_app
from flask_socketio import SocketIO, emit, send
from cerf7.db import db


socketio = SocketIO()


@socketio.on("message")
def handle_message(data):
    current_app.logger.debug("Got message from WebSocket: " + data)


@socketio.on("connect")
def handle_connection():
    send("Greetings!")


def init_app(app):
    socketio.init_app(app)
