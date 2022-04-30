import cerf7.socketio as socketio
import cerf7.rts as rts
import cerf7.dispatch as dispatch

from datetime import datetime, timedelta
from cerf7.db import *


class Storyline:
    def __init__(self, user: User):
        self.user = user

    def bootstrap(self) -> None:
        initial_state = InitialInGameState.query.first()
        user_state = InGameState(self.user, initial_state)
        db.session.add(user_state)

        for scheduling_precept in InitialScheduling.query.all():
            scheduled_event = ScheduledEvent(
                user_id=self.user.user_id,
                event_id=scheduling_precept.event_id,
                publication_datetime=scheduling_precept.event_datetime)
            db.session.add(scheduled_event)

        db.session.commit()
        self.fastforward()

    def fastforward(self) -> None:
        self.dispatch_next_event()
        while not self.user.in_game_state.is_online:
            self.dispatch_next_event()

    def dispatch_next_event(self) -> None:
        scheduled_event = self.user.scheduled_events[0]

        self.time_travel_to(scheduled_event.publication_datetime)
        self.satisfy_rts_attitude(scheduled_event.event_reference.rts_attitude)

        event_type = scheduled_event.event_reference.event_type
        dispatcher_cls = dispatch.by_type[event_type]
        dispatcher = dispatcher_cls(self.user, scheduled_event.event_reference)
        dispatcher.dispatch()

        db.session.delete(scheduled_event)
        db.session.commit()

        continue_dispatching = \
            self.user.rts_wanted_by > 0 and \
            self.user.in_game_state.is_online
        if continue_dispatching:
            rts.schedule_event_dispatch(self.user)

    def time_travel_to(self, destination: datetime):
        self.user.in_game_state.datetime = destination
        socketio.send_time_travel(self.user)

    def time_travel_by(self, interval: timedelta):
        self.time_travel_to(self.user.in_game_state.datetime + interval)

    def satisfy_rts_attitude(self, rts_attitude: RTSAttitude) -> None:
        if rts_attitude == RTSAttitude.WANTS:
            self.user.rts_wanted_by += 1
            if self.user.rts_wanted_by == 1:
                # This event is the first in series that wants RTS.
                # We need to create a new sync point.
                self.user.sync_point_irl = datetime.now()
                self.user.sync_point_in_game = self.user.in_game_state.datetime
        elif rts_attitude == RTSAttitude.REVOKES:
            self.user.rts_wanted_by -= 1
            if self.user.rts_wanted_by == 0:
                # Remove last stored sync point.
                self.user.sync_point_irl = None
                self.user.sync_point_in_game = None
