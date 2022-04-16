from flask import session, g
from cerf7.db import (
    db, User, InitialUserInGameState, UserInGameState, InitialScheduling,
    ScheduledEvent, ScheduledEventExpiration, AddConversationEvent, EventType
)
from cerf7.socketio import notify_about_available_conversation


def user_bootstrap():
    initial_state = InitialUserInGameState.query.first()
    user_state = UserInGameState(g.user.userId, initial_state)
    db.session.add(user_state)

    for scheduling_precept in InitialScheduling.query.all():
        event = ScheduledEvent(
            userId=session["userId"], eventId=scheduling_precept.eventId,
            publicationDateTime=scheduling_precept.eventDateTime)
        db.session.add(event)

    db.session.commit()
    fastforward()


def schedule_event(scheduling_precept):
    pass


def fastforward():
    # Shift time to the earliest scheduled event and dispatch it
    # scheduled_event = user.scheduledEvents.pop()
    scheduled_event = g.user.scheduledEvents[0]
    dispatch_scheduled_event(scheduled_event)

    # Keep dispatching in-game events until main character is back online
    while not g.user.inGameState.mainCharacterIsOnline:
        scheduled_event = g.user.scheduledEvents[0]
        dispatch_scheduled_event(scheduled_event)


def dispatch_scheduled_event(scheduled_event: ScheduledEvent):
    g.user.inGameState.inGameDateTime = scheduled_event.publicationDateTime

    event_type = scheduled_event.event.eventType
    event_id = scheduled_event.event.eventId
    if event_type == EventType.MAIN_CHARACTER_OFFLINE:
        g.user.inGameState.mainCharacterIsOnline = False
    elif event_type == EventType.MAIN_CHARACTER_BACK_ONLINE:
        g.user.inGameState.mainCharacterIsOnline = True
    elif event_type == EventType.ADD_CONVERSATION:
        event = AddConversationEvent.query.get(event_id)
        conversation = event.conversation

        # Not implemented

    elif event_type == EventType.SHEDULED_EVENT_EXPIRATION:
        event = ScheduledEventExpiration.get(event_id)
        expired_event = ScheduledEvent.query.get(
            (g.user.userId, event.expiredEventId))
        expired_event.delete()

    db.session.delete(scheduled_event)
    db.session.commit()
