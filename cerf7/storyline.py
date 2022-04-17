import datetime
import json

from flask import session, g
from cerf7.socketio import send_available_message
import cerf7.real_time_scheduling as rts
from cerf7.db import (
    db, Conversation, InitialUserInGameState, UserInGameState,
    InitialScheduling, ScheduledEvent, ScheduledEventExpiration,
    AddConversationEvent, EventType, ConversationState, ConversationMessage,
    DialogMessage, AvailableMessage, User
)


# TODO: Split module into several submodules.


def user_bootstrap():
    initial_state = InitialUserInGameState.query.first()
    user_state = UserInGameState(g.user.user_id, initial_state)
    db.session.add(user_state)

    for scheduling_precept in InitialScheduling.query.all():
        event = ScheduledEvent(
            user_id=session["user_id"], event_id=scheduling_precept.event_id,
            publication_date_time=scheduling_precept.event_date_time)
        db.session.add(event)

    db.session.commit()
    fastforward()


def fastforward():
    # Shift time to the earliest scheduled event and dispatch it
    # scheduled_event = user.scheduledEvents.pop()
    scheduled_event = g.user.scheduled_events[0]
    dispatch_scheduled_event(scheduled_event)

    # Keep dispatching in-game events until main character is back online
    while not g.user.in_game_state.main_character_is_online:
        scheduled_event = g.user.scheduled_events[0]
        dispatch_scheduled_event(scheduled_event)


def update_in_game_date_time(user, new_datetime):
    user.in_game_state.in_game_date_time = new_datetime


def in_game_date_time() -> datetime.datetime:
    return g.user.in_game_state.in_game_date_time


def get_conversation_state(user: User, conversation: Conversation)\
        -> ConversationState:
    return ConversationState.query\
        .get((user.user_id, conversation.conversation_id))


def dispatch_scheduled_event(scheduled_event: ScheduledEvent):
    update_in_game_date_time(g.user, scheduled_event.publication_date_time)

    event_type = scheduled_event.event.event_type
    event_id = scheduled_event.event.evet_id
    if event_type == EventType.MAIN_CHARACTER_OFFLINE:
        g.user.in_game_state.main_character_is_online = False
    elif event_type == EventType.MAIN_CHARACTER_BACK_ONLINE:
        g.user.in_game_state.main_character_is_online = True
    elif event_type == EventType.ADD_CONVERSATION:
        event_to_dispatch = AddConversationEvent.query.get(event_id)
        conversation = event_to_dispatch.conversation
        commit_conversation(conversation)
        update_conversation(conversation)
    elif event_type == EventType.SHEDULED_EVENT_EXPIRATION:
        event_to_dispatch = ScheduledEventExpiration.get(event_id)
        expired_event = ScheduledEvent.query.get(
            (g.user.user_id, event_to_dispatch.expired_event_id))
        expired_event.delete()

    db.session.delete(scheduled_event)
    db.session.commit()


def commit_conversation(conversation: Conversation):
    conversation_state = ConversationState(
        user_id=g.user.user_id, conversation_id=conversation.conversation_id)
    db.session.add(conversation_state)
    db.session.commit()


def update_conversation(conversation: Conversation):
    conversation_state = get_conversation_state(conversation)
    next_messages = ConversationMessage.query\
        .filter_by(
            conversation_id=conversation.conversation_id,
            from_state=conversation_state.conversation_state).all()

    if not next_messages:
        # Since there are no more messages, the conversation has ended.
        # For now, it's time for aftermath scheduling.
        do_aftermath_scheduling(conversation)
    elif next_messages[0].sender_id is None:
        # Now it is main character's turn to say something.
        # We commit available message options in the DB and send notifications
        # about them to client.
        for message in next_messages:
            commit_available_message(message)
            send_available_message(message)
    else:
        # Schedule opponent message in real time
        rts.schedule_npc_message(next_messages[0])


def message_time_shift(message: ConversationMessage) -> datetime.timedelta:
    # TODO: Calculate time shift using character's typing habits.
    avg_typing_speed_chars_per_minute = 200

    typing_time =\
        len(message.message_json["text"]) / avg_typing_speed_chars_per_minute
    timedelta = datetime.timedelta(minutes=typing_time)

    return timedelta


def commit_message(user: User, message: ConversationMessage):
    message_instance = DialogMessage(user, message)
    db.session.add(message_instance)
    db.session.commit()

    return message_instance


def commit_available_message(message: ConversationMessage):
    available_message = AvailableMessage(g.user, message)
    db.session.add(available_message)
    db.session.commit()


def do_aftermath_scheduling(conversation: Conversation):
    pass


def schedule_event(scheduling_precept):
    pass
