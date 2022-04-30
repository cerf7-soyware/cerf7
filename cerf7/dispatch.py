import cerf7.socketio as socketio

from cerf7.db import *
from cerf7.conversations import ConversationHandle


class EventDispatcher:
    def __init__(self, user: User, event_reference: EventReference):
        self.user = user
        self.event_reference = event_reference

    def dispatch(self) -> None:
        raise NotImplementedError()


class OfflineDispatcher(EventDispatcher):
    def dispatch(self) -> None:
        self.user.in_game_state.is_online = False
        socketio.send_offline(self.user)


class OnlineDispatcher(EventDispatcher):
    def dispatch(self) -> None:
        self.user.in_game_state.is_online = True
        socketio.send_back_online(self.user)


class NewConversationDispatcher(EventDispatcher):
    def dispatch(self) -> None:
        event = NewConversationEvent.query.get(self.event_reference.event_id)
        conversation_handle = ConversationHandle(self.user, event.conversation)
        conversation_handle.commit()
        conversation_handle.update()


class NPCMessageDispatcher(EventDispatcher):
    def dispatch(self) -> None:
        event = NPCMessageEvent.query.get(self.event_reference.event_id)
        message = event.conversation_message
        conversation_handle = ConversationHandle(
            self.user, message.conversation)
        conversation_handle.commit_npc_message(message)


class ExpiredEventDispatcher(EventDispatcher):
    def dispatch(self) -> None:
        event = ScheduledEventExpiration.get(self.event_reference.event_id)
        expired_event = ScheduledEvent.query.get(
            (self.user.user_id, event.expired_event_id))
        expired_event.delete()
        db.session.commit()


by_type = {
    EventType.MAIN_CHARACTER_OFFLINE: OfflineDispatcher,
    EventType.MAIN_CHARACTER_BACK_ONLINE: OnlineDispatcher,
    EventType.NEW_CONVERSATION: NewConversationDispatcher,
    EventType.NPC_MESSAGE: NPCMessageDispatcher,
    EventType.SCHEDULED_EVENT_EXPIRATION: ExpiredEventDispatcher
}
