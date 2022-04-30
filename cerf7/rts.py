import cerf7.storyline as sl

from flask_apscheduler import APScheduler
from cerf7.db import db, User


# TODO: For now, scheduler object is duplicated via fork before the application
#  starts. Only one scheduler is enough, though, because APScheduler uses
#  ThreadPool/ProcessPool executor.


scheduler = APScheduler()


def schedule_event_dispatch(user: User) -> None:
    event_to_dispatch = user.scheduled_events[0]

    time_since_sync_point = \
        event_to_dispatch.publication_datetime - \
        user.in_game_state.sync_point_in_game
    irl_publication_datetime = \
        user.in_game_state.sync_point_irl + \
        time_since_sync_point

    def task():
        with scheduler.app.app_context():
            db.session.add(user)
            storyline = sl.Storyline(user)
            storyline.dispatch_next_event()

    scheduler.add_job(
        "deferred-event-dispatch", func=task, trigger="date",
        run_date=irl_publication_datetime)


def init_app(app):
    scheduler.init_app(app)
