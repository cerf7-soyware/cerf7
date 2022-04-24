from datetime import datetime, timedelta
from typing import Callable, List
from flask_apscheduler import APScheduler
from cerf7.db import db, User


scheduler = APScheduler()


class RTSTask:
    def __init__(
            self, user: User, task_id: str, func: Callable[[], None],
            defer_by: timedelta, referred_db_entities: List[db.Model] = None):
        self.user = user
        self.id = task_id
        self.func = func

        self.irl_publication_time = datetime.now() + defer_by
        self.in_game_publication_time = \
            user.in_game_state.in_game_date_time + defer_by

        self.referred_db_entities = [] if referred_db_entities is None else \
            referred_db_entities

    def __call__(self, *args, **kwargs):
        print("Hello from APScheduler!")
        with scheduler.app.app_context():
            self._refresh_db_entities()
            self._update_in_game_datetime()
            self.func()

    def _refresh_db_entities(self):
        db.session.add(self.user)
        for entity in self.referred_db_entities:
            db.session.add(entity)

    def _update_in_game_datetime(self):
        self.user.in_game_state.in_game_date_time = \
            self.in_game_publication_time
        db.session.flush()


def schedule_task(task: RTSTask):
    scheduler.add_job(
        task.id, func=lambda: task(), trigger="date",
        run_date=task.irl_publication_time)


def init_app(app):
    scheduler.init_app(app)
