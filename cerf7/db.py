import click

from enum import Enum, auto, unique
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
from sqlalchemy.dialects import postgresql

db = SQLAlchemy()

# TODO: separate dynamically updated relations (e.g. per-user scheduled events
#  queue) from static data (structures defining the plot). Creating two
#  distinct databases for this purpose is considered.


DEFAULT_MODEL_STRING_LENGTH = 20
MODEL_PATH_LENGTH = 200


# Noinspection for ORM models is used because SQLAlchemy dynamically adds to
# `db` fields like Column, so PyCharm can't recognize them correctly.

################################################################################
# Dynamically updated relations
################################################################################

# noinspection PyUnresolvedReferences
class User(db.Model):
    PASSPHRASE_HASH_LENGTH = 64  # Hexadecimal SHA-256 hash length

    userId = db.Column(db.Integer, primary_key=True)
    passphraseHash = db.Column(db.String(PASSPHRASE_HASH_LENGTH),
                               nullable=False)


# noinspection PyUnresolvedReferences
class UserInGameState(db.Model):
    userId = db.Column(db.Integer, primary_key=True)

    inGameDateTime = db.Column(db.DateTime, nullable=False)
    activeConversationId = db.Column(db.Integer, nullable=True)
    activeConversationState = db.Column(db.Integer, nullable=True)
    datastore = db.Column(postgresql.JSONB, nullable=False, default="{}")
    mainCharacterIsOnline = db.Column(db.Boolean, nullable=False, default=True)


# noinspection PyUnresolvedReferences
class AvailableConversation(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    conversationId = db.Column(db.Integer, primary_key=True)


# noinspection PyUnresolvedReferences
class ConversationAftermath(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    conversationId = db.Column(db.Integer, primary_key=True)

    endingState = db.Column(db.Integer, nullable=False)


# noinspection PyUnresolvedReferences
class ScheduledEvent(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    eventId = db.Column(db.Integer, primary_key=True)

    publicationDateTime = db.Column(db.DateTime)


# noinspection PyUnresolvedReferences
class DialogMessage(db.Model):
    # All messages generated as user plays are committed into this relation.
    # This is required to support unique per-user plots.

    userId = db.Column(db.Integer, primary_key=True)
    opponentId = db.Column(db.Integer, primary_key=True)
    messageId = db.Column(db.Integer, primary_key=True)

    messageJson = db.Column(postgresql.JSONB, nullable=False)
    sentDateTime = db.Column(db.DateTime, nullable=False)
    senderId = db.Column(db.Integer, nullable=False)

    isRead = db.Column(db.Boolean, nullable=False)
    isEdited = db.Column(db.Boolean, nullable=False)


################################################################################
# Static data
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


# noinspection PyUnresolvedReferences
class CharacterProfileInfo(db.Model):
    # Here come VK-specific character attributes displayed in user profile,
    # e.g. interests, favourite quotes, attitude to smoking etc.

    characterId = db.Column(db.Integer, primary_key=True)

    # TODO: add VK-specific attributes


################################################################################

# noinspection PyUnresolvedReferences
class Conversation(db.Model):
    conversationId = db.Column(db.Integer, primary_key=True)
    opponentId = db.Column(db.Integer, primary_key=True)

    # Required conversations are those which push forward the plot.
    isRequired = db.Column(db.Boolean, nullable=False)


# noinspection PyUnresolvedReferences
class ConversationMessage(db.Model):
    conversationId = db.Column(db.Integer, primary_key=True)
    fromState = db.Column(db.Integer, primary_key=True)
    toState = db.Column(db.Integer, primary_key=True)

    senderId = db.Column(db.Integer, nullable=True)
    messageJson = db.Column(postgresql.JSONB, nullable=False)


# noinspection PyUnresolvedReferences
class ConversationTerminalState(db.Model):
    conversationId = db.Column(db.Integer, primary_key=True)
    conversationState = db.Column(db.Integer, primary_key=True)


################################################################################

@unique
class EventTypes(Enum):
    ADD_CONVERSATION = auto()
    REMOVE_CONVERSATION = auto()
    MAIN_CHARACTER_OFFLINE = auto()
    MAIN_CHARACTER_BACK_ONLINE = auto()


# noinspection PyUnresolvedReferences
class EventType(db.Model):
    eventId = db.Column(db.Integer, primary_key=True)
    eventType = db.Column(db.Enum(EventTypes), nullable=False)


# noinspection PyUnresolvedReferences
class AddConversationEvent(db.Model):
    eventId = db.Column(db.Integer, primary_key=True)
    conversationId = db.Column(db.Integer, nullable=False)


# noinspection PyUnresolvedReferences
class RemoveConversationEvent(db.Model):
    eventId = db.Column(db.Integer, primary_key=True)
    conversationId = db.Column(db.Integer, nullable=False)


################################################################################

# noinspection PyUnresolvedReferences
class AftermathDatastoreUpdate(db.Model):
    conversationId = db.Column(db.Integer, primary_key=True)
    endingState = db.Column(db.Integer, primary_key=True)
    updateExpression = db.Column(db.Text, nullable=False)


# noinspection PyUnresolvedReferences
class AftermathScheduling(db.Model):
    conversationId = db.Column(db.Integer, primary_key=True)
    endingState = db.Column(db.Integer, primary_key=True)
    eventId = db.Column(db.Integer, nullable=False)
    eventDateTime = db.Column(db.Integer, nullable=False)
    datastorePredicate = db.Column(db.Text, nullable=False, default="True")

################################################################################


def init_db():
    db.drop_all()
    db.create_all()


@click.command("init-db")
@with_appcontext
def init_db_command():
    if click.confirm(
            "This command fully removes existing database and recreates empty "
            "tables. Do you want to proceed?"
    ):
        init_db()
        click.echo("Successfully initialized the database")


def init_app(app):
    db.init_app(app)
    app.cli.add_command(init_db_command)
