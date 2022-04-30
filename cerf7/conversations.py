import cerf7.socketio as socketio

from typing import List
from datetime import timedelta
from cerf7.db import *
from cerf7.storyline import Storyline


class ConversationHandle:
    def __init__(self, user: User, conversation: Conversation):
        self.user = user
        self.conversation = conversation

    def commit(self) -> None:
        self.user.commit_new_conversation(self.conversation)

    def update(self) -> None:
        next_messages = self._next_messages()
        if not next_messages:
            # Since there are no more messages, the conversation has ended.
            # For now, it's time for aftermath scheduling.
            self._do_aftermath_scheduling()
        elif next_messages[0].sender_id is None:
            # Now it is main character's turn to say something.
            # We send notifications about the available options to frontend.
            for message in next_messages:
                socketio.send_available_message(self.user, message)
        else:
            npc_message = next_messages[0]
            self._schedule_npc_message(npc_message)

    def commit_npc_message(self, message: ConversationMessage) -> None:
        message_instance = self.user.commit_message(message)
        state_entity = self._conversation_state()
        state_entity.conversation_state = message.to_state

        socketio.send_npc_message(self.user, message_instance)
        self.update()

    def follow_user_choice(self, from_state: int, to_state: int) -> None:
        message = ConversationMessage.query.get(
            (self.conversation.conversation_id, from_state, to_state))
        state_entity = self._conversation_state()

        state_entity.conversation_state = message.to_state
        self.user.commit_message(message)

        storyline = Storyline(self.user)
        storyline.time_travel_by(self._message_time_shift(message))

        self.update()

    def _do_aftermath_scheduling(self) -> None:
        raise NotImplementedError()

    def _schedule_npc_message(self, message: ConversationMessage) -> None:
        typing_time = self._message_time_shift(message)
        publication_datetime = \
            self.user.in_game_state.datetime + \
            typing_time

        scheduled_event = ScheduledEvent(
            user_id=self.user.user_id,
            event_id=message.npc_message_event.event_id,
            publication_datetime=publication_datetime)

        db.session.add(scheduled_event)
        db.session.commit()

    def _conversation_state(self) -> ConversationState:
        return ConversationState.query \
            .get((self.user.user_id, self.conversation.conversation_id))

    def _next_messages(self) -> List[ConversationMessage]:
        state_entity = self._conversation_state()
        return ConversationMessage.query \
            .filter_by(
                conversation_id=self.conversation.conversation_id,
                from_state=state_entity.conversation_state).all()

    @staticmethod
    def _message_time_shift(message: ConversationMessage) -> timedelta:
        # TODO: Calculate time shift using character's typing habits.
        typing_speed_chars_per_min = 400

        text_len = len(message.message_body["text"])
        typing_time = timedelta(minutes=text_len / typing_speed_chars_per_min)
        lag = timedelta(seconds=0.1)

        return lag + typing_time
