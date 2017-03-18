import time
import datetime
import traceback

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from celery.utils.log import get_logger
from celery.beat import Scheduler, event_t, heapq

from server.models.celery import PeriodicTask
from server.modules.celery.beat.entry import SAScheduleEntry
from server.instance.celery_config import CELERY_BEAT_DB_URI


class SAScheduler(Scheduler):
    UPDATE_INTERVAL = datetime.timedelta(seconds=2)

    Entry = SAScheduleEntry

    Model = PeriodicTask

    def __init__(self, *args, **kwargs):
        self.db_uri = CELERY_BEAT_DB_URI
        self.db_engine = create_engine(self.db_uri)
        self.session = scoped_session(sessionmaker(bind=self.db_engine))

        self.query = self.session.query

        self._schedule = {}
        self._last_updated = None
        Scheduler.__init__(self, *args, **kwargs)
        self.max_interval = (kwargs.get('max_interval')
                             or self.app.conf.CELERYBEAT_MAX_LOOP_INTERVAL or 5)

    def tick(self, event_t=event_t, min=min,
             heappop=heapq.heappop, heappush=heapq.heappush,
             heapify=heapq.heapify, mktime=time.mktime):

        adjust = self.adjust
        interval = self.max_interval

        for entry in self.schedule.values():
            is_due, next_time_to_run = self.is_due(entry)
            if is_due:
                self.apply_entry(entry, producer=self.producer)
            interval = min(adjust(next_time_to_run), interval)
        return interval

    def setup_schedule(self):
        pass

    def requires_update(self):
        if not self._last_updated:
            return True
        return self._last_updated + self.UPDATE_INTERVAL < datetime.datetime.now()

    @property
    def objects(self):
        objs = self.query(self.Model).filter_by(enabled=True).all()
        return objs

    def get_from_database(self):
        self.sync()
        records = {}
        for obj in self.objects:
            records[obj.name] = self.Entry(obj)
        return records

    @property
    def schedule(self):
        if self.requires_update():
            self._schedule = self.get_from_database()
            self._last_updated = datetime.datetime.now()
        return self._schedule

    def sync(self):
        for entry in self._schedule.values():
            try:
                if entry.total_run_count > entry._task.total_run_count:
                    entry._task.total_run_count = entry.total_run_count
                if entry.last_run_at and entry._task.last_run_at and entry.last_run_at > entry._task.last_run_at:
                    entry._task.last_run_at = entry.last_run_at
                entry._task.run_immediately = False
                self.session.commit()
            except Exception:
                get_logger(__name__).error(traceback.format_exc())
