from datetime import timedelta
from cerf7.socketio import send_available_message, send_npc_message
from cerf7.real_time_scheduling import RTSTask, schedule_task
from cerf7.db import *


class Storyline:
    def __init__(self, user: User):
        self.user = user

    def bootstrap(self) -> None:
        initial_state = InitialUserInGameState.query.first()
        user_state = UserInGameState(self.user.user_id, initial_state)
        db.session.add(user_state)

        for scheduling_precept in InitialScheduling.query.all():
            event = ScheduledEvent(
                user_id=self.user.user_id,
                event_id=scheduling_precept.event_id,
                publication_date_time=scheduling_precept.event_date_time)
            db.session.add(event)

        db.session.commit()
        self.fastforward()

    def fastforward(self) -> None:
        # Shift time to the earliest scheduled event and dispatch it
        # scheduled_event = user.scheduledEvents.pop()
        scheduled_event = self.user.scheduled_events[0]
        self.dispatch_scheduled_event(scheduled_event)

        # Keep dispatching in-game events until main character is back online
        while not self.user.in_game_state.main_character_is_online:
            scheduled_event = self.user.scheduled_events[0]
            self.dispatch_scheduled_event(scheduled_event)

    def dispatch_scheduled_event(self, scheduled_event: ScheduledEvent) -> None:
        self.user.in_game_state.in_game_date_time = \
            scheduled_event.publication_date_time

        event_type = scheduled_event.event.event_type
        event_id = scheduled_event.event.event_id

        # Grab event information from events table depending on `event_type` and
        # push forward the plot.
        if event_type == EventType.MAIN_CHARACTER_OFFLINE:
            self.user.in_game_state.main_character_is_online = False
        elif event_type == EventType.MAIN_CHARACTER_BACK_ONLINE:
            self.user.in_game_state.main_character_is_online = True
        elif event_type == EventType.ADD_CONVERSATION:
            event_to_dispatch = AddConversationEvent.query.get(event_id)
            conversation = ConversationHandle(
                self.user, event_to_dispatch.conversation)
            conversation.commit()
            conversation.update()
        elif event_type == EventType.SHEDULED_EVENT_EXPIRATION:
            event_to_dispatch = ScheduledEventExpiration.get(event_id)
            expired_event = ScheduledEvent.query.get(
                (self.user.user_id, event_to_dispatch.expired_event_id))
            expired_event.delete()

        db.session.delete(scheduled_event)
        db.session.commit()


class ConversationHandle:
    def __init__(self, user: User, conversation: Conversation):
        self.user = user
        self.conversation = conversation

    def commit(self) -> None:
        self.user.commit_new_conversation(self.conversation)

    def update(self) -> None:
        conversation_state = self._get_conversation_state()
        next_messages = ConversationMessage.query \
            .filter_by(
                conversation_id=self.conversation.conversation_id,
                from_state=conversation_state.conversation_state).all()

        if not next_messages:
            # Since there are no more messages, the conversation has ended.
            # For now, it's time for aftermath scheduling.
            self._do_aftermath_scheduling()
        elif next_messages[0].sender_id is None:
            # Now it is main character's turn to say something.
            # We commit available message options in the DB and send
            # notifications # about them to client.
            for message in next_messages:
                self.user.commit_available_message(message)
                send_available_message(self.user, message)
        else:
            # Schedule opponent's message in real time

            npc_message = next_messages[0]
            typing_time = self._message_time_shift(npc_message)

            def action():
                message_instance = self.user.commit_message(npc_message)
                conversation_state.conversation_state = npc_message.to_state
                db.session.flush()

                send_npc_message(self.user, message_instance)
                self.update()

            task = RTSTask(
                self.user, "npc-message", action, typing_time,
                [npc_message, conversation_state, self.conversation])
            schedule_task(task)

    def _do_aftermath_scheduling(self) -> None:
        pass

    def _get_conversation_state(self) -> ConversationState:
        return ConversationState.query \
            .get((self.user.user_id, self.conversation.conversation_id))

    @staticmethod
    def _message_time_shift(message: ConversationMessage) -> timedelta:
        # TODO: Calculate time shift using character's typing habits.
        typing_speed_chars_per_min = 200

        text_len = len(message.message_body["text"])
        typing_time = text_len / typing_speed_chars_per_min

        return timedelta(minutes=typing_time) + timedelta(seconds=0.3)
