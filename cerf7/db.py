import click
import json

from functools import partial
from dataclasses import dataclass
from enum import Enum, auto, unique
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship, backref


db = SQLAlchemy(
    engine_options={
        "json_serializer": partial(json.dumps, ensure_ascii=False)})


# TODO: Separate dynamically updated relations (e.g. per-user scheduled events
#  queue) from static data (structures defining the plot). Creating two
#  distinct databases for this purpose is considered.


# TODO: Setup model inheritance to avoid code duplication between
#  static/dynamic models.


DEFAULT_MODEL_STRING_LENGTH = 50
MODEL_PATH_LENGTH = 200


# Noinspection for ORM models is used because SQLAlchemy dynamically adds to
# `db` fields like Column, so PyCharm can't recognize them correctly.

################################################################################
# Dynamically updated relations
################################################################################

# noinspection PyUnresolvedReferences
class User(db.Model):
    SID_LENGTH = 20

    user_id = db.Column(db.Integer, primary_key=True)
    passphrase = db.Column(
        db.String(DEFAULT_MODEL_STRING_LENGTH), nullable=False, unique=True)

    # SocketIO identifier
    current_sid = db.Column(db.String(SID_LENGTH), nullable=True, unique=True)

    # Real-time scheduling
    rts_wanted_by = db.Column(db.Integer, nullable=False, default=0)
    sync_point_irl = db.Column(db.DateTime, nullable=True)
    sync_point_in_game = db.Column(db.DateTime, nullable=True)

    in_game_state = relationship("InGameState", uselist=False)
    conversation_state = relationship("ConversationState")
    messages = relationship("DialogMessage")
    scheduled_events = relationship(
        "ScheduledEvent", order_by="ScheduledEvent.publication_datetime")

    def commit_new_conversation(self, conversation: "Conversation") -> None:
        conversation_state = ConversationState(
            user_id=self.user_id,
            conversation_id=conversation.conversation_id,
            conversation_state=0)
        db.session.add(conversation_state)
        db.session.commit()

    def commit_message(self, message: "ConversationMessage") -> "DialogMessage":
        message_instance = DialogMessage(self, message)
        db.session.add(message_instance)
        db.session.commit()

        return message_instance


# noinspection PyUnresolvedReferences
class InGameState(db.Model):
    user_id = db.Column(
        db.Integer, ForeignKey("user.user_id"), primary_key=True)

    datetime = db.Column(db.DateTime, nullable=False)
    datastore = db.Column(postgresql.JSONB, nullable=False)
    is_online = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, user: "User", initial_state: "InitialInGameState"):
        self.user_id = user.user_id
        self.datetime = initial_state.datetime
        self.datastore = initial_state.datastore
        self.is_online = initial_state.is_online


# noinspection PyUnresolvedReferences
class ConversationState(db.Model):
    user_id = db.Column(
        db.Integer, ForeignKey("user.user_id"), primary_key=True)
    conversation_id = db.Column(
        db.Integer, ForeignKey("conversation.conversation_id"),
        primary_key=True)

    conversation_state = db.Column(db.Integer, nullable=False)


# noinspection PyUnresolvedReferences
class ScheduledEvent(db.Model):
    user_id = db.Column(
        db.Integer, ForeignKey("user.user_id"), primary_key=True)
    event_id = db.Column(
        db.Integer, ForeignKey("event_reference.event_id"), primary_key=True)

    publication_datetime = db.Column(db.DateTime)

    event_reference = relationship("EventReference", uselist=False)


# noinspection PyUnresolvedReferences
@dataclass
class DialogMessage(db.Model):
    # All messages that are generated as user plays are committed into this
    # relation. This is required to support unique per-user plots.

    user_id: int = db.Column(
        db.Integer, ForeignKey("user.user_id"), primary_key=True)
    opponent_id: int = db.Column(
        db.Integer, ForeignKey("character.character_id"), primary_key=True)
    message_id: int = db.Column(
        db.Integer, primary_key=True, autoincrement=True)

    message_body: dict = db.Column(postgresql.JSONB, nullable=False)
    sent_datetime: str = db.Column(db.DateTime, nullable=False)
    sender_id: int = db.Column(db.Integer, nullable=True)
    is_read: bool = db.Column(db.Boolean, nullable=False, default=False)
    is_edited: bool = db.Column(db.Boolean, nullable=False, default=False)

    opponent = relationship("Character", uselist=False)

    def __init__(
            self, user: "User", conversation_message: "ConversationMessage"):
        self.user_id = user.user_id
        self.opponent_id = conversation_message.conversation.opponent_id
        self.message_body = conversation_message.message_body
        self.sent_datetime = user.in_game_state.datetime
        self.sender_id = conversation_message.sender_id


################################################################################
# Static data
################################################################################

# noinspection PyUnresolvedReferences
class InitialInGameState(db.Model):
    # For ep0, only one initial state of the game world exists.
    # In further episodes, user might start from different initial states
    # depending on the previous episode ending.
    initial_state_id = db.Column(db.Integer, primary_key=True)

    datetime = db.Column(db.DateTime, nullable=False)
    active_conversation_state = db.Column(db.Integer, nullable=True)
    datastore = db.Column(postgresql.JSONB, nullable=False)
    is_online = db.Column(
        db.Boolean, nullable=False, default=False)
    active_conversation_id = db.Column(
        db.Integer, ForeignKey("conversation.conversation_id"), nullable=True)


################################################################################

# noinspection PyUnresolvedReferences
class Character(db.Model):
    character_id = db.Column(db.Integer, primary_key=True)

    # vk.com/alexcreepman
    handle = db.Column(
        db.String(DEFAULT_MODEL_STRING_LENGTH), unique=True, nullable=False)

    first_name = db.Column(
        db.String(DEFAULT_MODEL_STRING_LENGTH), nullable=False)
    middle_name = db.Column(
        db.String(DEFAULT_MODEL_STRING_LENGTH), nullable=True)
    last_name = db.Column(
        db.String(DEFAULT_MODEL_STRING_LENGTH), nullable=False)

    profile_info = relationship("CharacterProfileInfo", uselist=False)


# noinspection PyUnresolvedReferences
class CharacterProfileInfo(db.Model):
    # Here come VK-specific character attributes displayed in user profile,
    # e.g. interests, favourite quotes, attitude to smoking etc.

    character_id = db.Column(
        db.Integer, ForeignKey("character.character_id"), primary_key=True)

    # TODO: Add VK-specific attributes.


################################################################################

# noinspection PyUnresolvedReferences
class PrePlotDialogMessage(db.Model):
    # There are some messages that had been sent before the story began.
    # These messages are the same for all users.

    opponent_id = db.Column(
        db.Integer, ForeignKey("character.character_id"), primary_key=True)
    message_id = db.Column(db.Integer, primary_key=True)

    message_body = db.Column(postgresql.JSONB, nullable=False)
    sent_datetime = db.Column(db.DateTime, nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False)
    is_edited = db.Column(db.Boolean, nullable=False)

    opponent = relationship("Character", uselist=False)


################################################################################

# noinspection PyUnresolvedReferences
class Conversation(db.Model):
    conversation_id = db.Column(db.Integer, primary_key=True)
    opponent_id = db.Column(db.Integer, ForeignKey("character.character_id"))

    # Required conversations are those which push forward the plot
    is_required = db.Column(db.Boolean, nullable=False)

    opponent = relationship("Character", uselist=False)
    messages = relationship("ConversationMessage")
    aftermath_datastore_updates = relationship("AftermathDatastoreUpdate")
    aftermath_scheduling = relationship("AftermathScheduling")


# noinspection PyUnresolvedReferences
@dataclass
class ConversationMessage(db.Model):
    conversation_id: int = db.Column(
        db.Integer, ForeignKey("conversation"), primary_key=True)
    from_state: int = db.Column(db.Integer, primary_key=True)
    to_state: int = db.Column(db.Integer, primary_key=True)

    message_body: dict = db.Column(postgresql.JSONB, nullable=False)
    sender_id: int = db.Column(
        db.Integer, ForeignKey("character.character_id"), nullable=True)

    sender = relationship("Character", uselist=False)
    conversation = relationship("Conversation", uselist=False)


################################################################################

# TODO: Agree on complete event type list.

@unique
class EventType(Enum):
    NEW_CONVERSATION = auto()
    NPC_MESSAGE = auto()
    SCHEDULED_EVENT_EXPIRATION = auto()
    MAIN_CHARACTER_OFFLINE = auto()
    MAIN_CHARACTER_BACK_ONLINE = auto()


@unique
class RTSAttitude(Enum):
    WANTS = auto()
    REVOKES = auto()
    NEUTRAL = auto()


# noinspection PyUnresolvedReferences
class EventReference(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.Enum(EventType), nullable=False)
    rts_attitude = db.Column(
        db.Enum(RTSAttitude), nullable=False, server_default="NEUTRAL")


# noinspection PyUnresolvedReferences
class NewConversationEvent(db.Model):
    event_id = db.Column(
        db.Integer, ForeignKey("event_reference.event_id"), primary_key=True)
    conversation_id = db.Column(
        db.Integer, ForeignKey("conversation.conversation_id"))

    conversation = relationship("Conversation")


# noinspection PyUnresolvedReferences
class NPCMessageEvent(db.Model):
    event_id = db.Column(
        db.Integer, ForeignKey("event_reference.event_id"), primary_key=True)

    conversation_id: int = db.Column(db.Integer)
    from_state: int = db.Column(db.Integer)
    to_state: int = db.Column(db.Integer)

    event_reference = relationship("EventReference", uselist=False)
    conversation_message = relationship(
        "ConversationMessage", uselist=False,
        backref=backref("npc_message_event", uselist=False))

    __table_args__ = [ForeignKeyConstraint(
        (conversation_id, from_state, to_state),
        ("conversation_message.conversation_id",
         "conversation_message.from_state",
         "conversation_message.to_state"))]


# noinspection PyUnresolvedReferences
class ScheduledEventExpiration(db.Model):
    event_id = db.Column(
        db.Integer, ForeignKey("event_reference.event_id"), primary_key=True)
    expired_event_id = db.Column(
        db.Integer, ForeignKey("event_reference.event_id"))


################################################################################

# noinspection PyUnresolvedReferences
class InitialScheduling(db.Model):
    scheduling_id = db.Column(db.Integer, primary_key=True)

    # Here are the events that need to be scheduled before the story starts.
    # E.g. the first conversation in the story needs to be scheduled from here.
    event_datetime = db.Column(db.DateTime, nullable=False)
    event_id = db.Column(
        db.Integer, ForeignKey("event_reference.event_id"), nullable=False)


# noinspection PyUnresolvedReferences
class AftermathDatastoreUpdate(db.Model):
    conversation_id = db.Column(
        db.Integer, ForeignKey("conversation.conversation_id"),
        primary_key=True)
    ending_state = db.Column(db.Integer, primary_key=True)

    update_expression = db.Column(db.Text, nullable=False)


# noinspection PyUnresolvedReferences
class AftermathScheduling(db.Model):
    conversation_id = db.Column(
        db.Integer, ForeignKey("conversation.conversation_id"),
        primary_key=True)
    ending_state = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(
        db.Integer, ForeignKey("event_reference.event_id"), nullable=False)
    event_datetime = db.Column(db.Integer, nullable=False)
    datastore_predicate = db.Column(db.Text, nullable=False, default="True")

    event_reference = relationship("EventReference", uselist=False)


################################################################################

def init_db():
    db.drop_all()
    db.create_all()


@click.command("init-db")
@with_appcontext
def init_db_command():
    if click.confirm(
            "This command fully removes existing database and recreates empty "
            "tables. Do you want to proceed?"):
        init_db()
        click.echo("Successfully initialized the database.")


def init_app(app):
    db.init_app(app)
    app.cli.add_command(init_db_command)
