from flask import current_app
from flask_socketio import SocketIO
from cerf7.db import db


socketio = SocketIO()


@socketio.on("message")
def handle_message(data):
    current_app.logger.debug("Got message from WebSocket: " + data)
