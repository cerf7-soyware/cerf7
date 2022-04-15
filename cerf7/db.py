import click

from enum import Enum, auto, unique
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship


db = SQLAlchemy()


# TODO: separate dynamically updated relations (e.g. per-user scheduled events
#  queue) from static data (structures defining the plot). Creating two
#  distinct databases for this purpose is considered.

# TODO: setup model inheritance to avoid code duplication between
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
    userId = db.Column(db.Integer, primary_key=True)
    passphrase = db.Column(
        db.String(DEFAULT_MODEL_STRING_LENGTH), nullable=False, unique=True)

    inGameState = relationship(
        "UserInGameState", uselist=False, lazy="select")
    availableConversations = relationship(
        "AvailableConversation", lazy="select")
    conversationAftermaths = relationship(
        "ConversationAftermath", lazy="select")
    scheduledEvents = relationship(
        "ScheduledEvent", order_by="ScheduledEvent.publicationDateTime",
        lazy="select")
    messages = relationship("DialogMessage", lazy="select")


# noinspection PyUnresolvedReferences
class UserInGameState(db.Model):
    userId = db.Column(db.Integer, ForeignKey("user.userId"), primary_key=True)

    inGameDateTime = db.Column(db.DateTime, nullable=False)
    activeConversationId = db.Column(
        db.Integer, ForeignKey("conversation.conversationId"), nullable=True)
    activeConversationState = db.Column(db.Integer, nullable=True)
    datastore = db.Column(postgresql.JSONB, nullable=False)
    mainCharacterIsOnline = db.Column(db.Boolean, nullable=False, default=False)

    activeConversation = relationship(
        "Conversation", uselist=False, lazy="select")

    def __init__(self, user_id, initial_state: "InitialUserInGameState"):
        self.userId = user_id
        self.inGameDateTime = initial_state.inGameDateTime
        self.activeConversationId = initial_state.activeConversationId
        self.activeConversationState = initial_state.activeConversationState
        self.datastore = initial_state.datastore
        self.mainCharacterIsOnline = initial_state.mainCharacterIsOnline


# noinspection PyUnresolvedReferences
class AvailableConversation(db.Model):
    userId = db.Column(db.Integer, ForeignKey("user.userId"), primary_key=True)
    conversationId = db.Column(
        db.Integer, ForeignKey("conversation.conversationId"), primary_key=True)

    conversation = relationship("Conversation", uselist=False, lazy="select")


# noinspection PyUnresolvedReferences
class ConversationAftermath(db.Model):
    userId = db.Column(db.Integer, ForeignKey("user.userId"), primary_key=True)
    conversationId = db.Column(
        db.Integer, ForeignKey("conversation.conversationId"), primary_key=True)
    endingState = db.Column(db.Integer, nullable=False)


# noinspection PyUnresolvedReferences
class ScheduledEvent(db.Model):
    userId = db.Column(db.Integer, ForeignKey("user.userId"), primary_key=True)
    eventId = db.Column(
       db.Integer, ForeignKey("event.eventId"), primary_key=True)
    publicationDateTime = db.Column(db.DateTime)

    # There is no relationship `event` but only `eventType` because
    # information about events of different types is stored in separate
    # relations.
    event = relationship("Event", uselist=False, lazy="select")


# noinspection PyUnresolvedReferences
class DialogMessage(db.Model):
    # All messages that are generated as user plays are committed into this
    # relation. This is required to support unique per-user plots.

    userId = db.Column(db.Integer, ForeignKey("user.userId"), primary_key=True)
    opponentId = db.Column(
        db.Integer, ForeignKey("character.characterId"), primary_key=True)
    messageId = db.Column(db.Integer, primary_key=True)

    messageJson = db.Column(postgresql.JSONB, nullable=False)
    sentDateTime = db.Column(db.DateTime, nullable=False)
    senderId = db.Column(db.Integer, nullable=False)

    isRead = db.Column(db.Boolean, nullable=False)
    isEdited = db.Column(db.Boolean, nullable=False)

    opponent = relationship("Character", uselist=False, lazy="select")


################################################################################
# Static data
################################################################################

# noinspection PyUnresolvedReferences
class InitialUserInGameState(db.Model):
    # For ep0, only one initial state of the game world exists.
    # In further episodes, user might start from different initial states
    # depending on the previous episode ending.
    initialStateId = db.Column(db.Integer, primary_key=True)

    inGameDateTime = db.Column(db.DateTime, nullable=False)
    activeConversationId = db.Column(
        db.Integer, ForeignKey("conversation.conversationId"), nullable=True)
    activeConversationState = db.Column(db.Integer, nullable=True)
    datastore = db.Column(postgresql.JSONB, nullable=False)
    mainCharacterIsOnline = db.Column(db.Boolean, nullable=False, default=False)


################################################################################

# noinspection PyUnresolvedReferences
class Character(db.Model):
    characterId = db.Column(db.Integer, primary_key=True)

    # vk.com/alexcreepman
    handle = db.Column(db.String(DEFAULT_MODEL_STRING_LENGTH), unique=True,
                       nullable=False)

    firstName = db.Column(db.String(DEFAULT_MODEL_STRING_LENGTH),
                          nullable=False)
    middleName = db.Column(db.String(DEFAULT_MODEL_STRING_LENGTH),
                           nullable=True)
    lastName = db.Column(db.String(DEFAULT_MODEL_STRING_LENGTH),
                         nullable=False)

    profileInfo = relationship(
        "CharacterProfileInfo", uselist=False, lazy="select")


# noinspection PyUnresolvedReferences
class CharacterProfileInfo(db.Model):
    # Here come VK-specific character attributes displayed in user profile,
    # e.g. interests, favourite quotes, attitude to smoking etc.

    characterId = db.Column(
        db.Integer, ForeignKey("character.characterId"), primary_key=True)

    # TODO: add VK-specific attributes


################################################################################

# noinspection PyUnresolvedReferences
class PrePlotDialogMessage(db.Model):
    # There are some messages that had been sent before the story began.
    # These messages are the same for all users.

    opponentId = db.Column(
        db.Integer, ForeignKey("character.characterId"), primary_key=True)
    messageId = db.Column(db.Integer, primary_key=True)

    messageJson = db.Column(postgresql.JSONB, nullable=False)
    sentDateTime = db.Column(db.DateTime, nullable=False)
    senderId = db.Column(db.Integer, nullable=False)

    isRead = db.Column(db.Boolean, nullable=False)
    isEdited = db.Column(db.Boolean, nullable=False)

    opponent = relationship("Character", uselist=False, lazy="select")


################################################################################

# noinspection PyUnresolvedReferences
class Conversation(db.Model):
    conversationId = db.Column(db.Integer, primary_key=True)
    opponentId = db.Column(db.Integer, ForeignKey("character.characterId"))

    # Required conversations are those which push forward the plot
    isRequired = db.Column(db.Boolean, nullable=False)

    opponent = relationship("Character", uselist=False, lazy="select")
    messages = relationship("ConversationMessage", lazy="select")
    terminalStates = relationship("ConversationTerminalState", lazy="select")
    aftermathDatastoreUpdates = relationship(
        "AftermathDatastoreUpdate", lazy="select")
    aftermathScheduling = relationship(
        "AftermathScheduling", lazy="select")


# noinspection PyUnresolvedReferences
class ConversationMessage(db.Model):
    conversationId = db.Column(
        db.Integer, ForeignKey("conversation"), primary_key=True)
    fromState = db.Column(db.Integer, primary_key=True)
    toState = db.Column(db.Integer, primary_key=True)

    senderId = db.Column(
        db.Integer, ForeignKey("character.characterId"), nullable=True)
    messageJson = db.Column(postgresql.JSONB, nullable=False)

    sender = relationship("Character", uselist=False, lazy="select")


# noinspection PyUnresolvedReferences
class ConversationTerminalState(db.Model):
    conversationId = db.Column(
        db.Integer, ForeignKey("conversation.conversationId"), primary_key=True)
    conversationState = db.Column(db.Integer, primary_key=True)


################################################################################

# TODO: agree on complete event type list.

@unique
class EventType(Enum):
    ADD_CONVERSATION = auto()
    SCHEDULED_EVENT_EXPIRATION = auto()
    MAIN_CHARACTER_OFFLINE = auto()
    MAIN_CHARACTER_BACK_ONLINE = auto()


# noinspection PyUnresolvedReferences
class Event(db.Model):
    eventId = db.Column(db.Integer, primary_key=True)
    eventType = db.Column(db.Enum(EventType), nullable=False)


# noinspection PyUnresolvedReferences
class AddConversationEvent(db.Model):
    eventId = db.Column(
        db.Integer, ForeignKey("event.eventId"), primary_key=True)
    conversationId = db.Column(
        db.Integer, ForeignKey("conversation.conversationId"))

    conversation = relationship("Conversation", lazy="select")


# noinspection PyUnresolvedReferences
class ScheduledEventExpiration(db.Model):
    eventId = db.Column(
        db.Integer, ForeignKey("event.eventId"), primary_key=True)
    expiredEventId = db.Column(
        db.Integer, ForeignKey("event.eventId"))


################################################################################

# noinspection PyUnresolvedReferences
class InitialScheduling(db.Model):
    schedulingId = db.Column(db.Integer, primary_key=True)

    # Here are the events that need to be scheduled before the story starts.
    # E.g. the first conversation in the story needs to be scheduled from here.
    eventId = db.Column(db.Integer, ForeignKey("event.eventId"), nullable=False)
    eventDateTime = db.Column(db.DateTime, nullable=False)


# noinspection PyUnresolvedReferences
class AftermathDatastoreUpdate(db.Model):
    conversationId = db.Column(
        db.Integer, ForeignKey("conversation.conversationId"), primary_key=True)
    endingState = db.Column(db.Integer, primary_key=True)
    updateExpression = db.Column(db.Text, nullable=False)


# noinspection PyUnresolvedReferences
class AftermathScheduling(db.Model):
    conversationId = db.Column(
        db.Integer, ForeignKey("conversation.conversationId"), primary_key=True)
    endingState = db.Column(db.Integer, primary_key=True)
    eventId = db.Column(db.Integer, ForeignKey("event.eventId"), nullable=False)
    eventDateTime = db.Column(db.Integer, nullable=False)
    datastorePredicate = db.Column(db.Text, nullable=False, default="True")

    event = relationship("Event", uselist=False, lazy="select")


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
