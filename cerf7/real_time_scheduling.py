import datetime

from flask_apscheduler import APScheduler
from flask import g
from cerf7.db import db, ConversationMessage, User
from cerf7.socketio import send_npc_message
import cerf7.storyline as sl


scheduler = APScheduler()


def schedule_npc_message(npc_message: ConversationMessage):
    time_shift = sl.message_time_shift(npc_message)
    irl_publication_datetime = datetime.datetime.now() + time_shift
    in_game_publication_datetime = sl.in_game_date_time() + time_shift
    user_id = g.user.user_id

    def publish_npc_message():
        with scheduler.app.app_context():
            print("From APScheduler")

            user = User.query.get(user_id)

            print("Got user")

            message_instance = sl.commit_message(user, npc_message)
            sl.update_in_game_date_time(user, in_game_publication_datetime)
            conversation_state = sl.get_conversation_state(
                user, npc_message.conversation)
            conversation_state.conversation_state = npc_message.to_state

            db.session.commit()

            send_npc_message(message_instance)
            sl.update_conversation(npc_message.conversation)

    scheduler.add_job(
        id="npc-message", func=publish_npc_message, trigger="date",
        run_date=irl_publication_datetime)


def init_app(app):
    scheduler.init_app(app)
