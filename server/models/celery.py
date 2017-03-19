import json
import datetime
from enum import Enum

from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
import celery.schedules

from server.utils import gen_uuid
from server.application.sqlalchemy_db import Model


class PERIODS(Enum):
    DAYS = 'days'
    HOURS = 'hours'
    MINUTES = 'minutes'
    SECONDS = 'seconds'
    MICROSECONDS = 'microseconds'


class TaskRole(Enum):
    CHORDS = 'chords'
    INITIALIZER = 'initializer'
    CALLBACK = 'callback'


ValidationError = type("ValidationError", (BaseException,), {})


class Interval(Model):
    __tablename__ = "interval"

    id = Column(Integer, primary_key=True)
    uuid = Column('uuid', String, nullable=False, unique=True, default=gen_uuid)
    _every = Column("every", Integer, default=0, nullable=False)
    _period = Column("period", String)

    @property
    def every(self):
        return self._every

    @every.setter
    def every(self, value):
        value = int(value)
        self._every = max(value, 0)

    @property
    def period(self):
        return PERIODS(self._period)

    @period.setter
    def period(self, value):
        if isinstance(value, PERIODS):
            self._period = value.value
        else:
            self._period = PERIODS(value).value

    @property
    def schedule(self):
        return celery.schedules.schedule(datetime.timedelta(**{self.period.value: self.every}))

    @property
    def period_singular(self):
        return self.period[:-1]


class Crontab(Model):
    __tablename__ = "crontab"

    id = Column(Integer, primary_key=True)
    uuid = Column('uuid', String, nullable=False, unique=True, default=gen_uuid)

    minute = Column(String, default='*', nullable=False)
    hour = Column(String, default='*', nullable=False)
    day_of_week = Column(String, default='*', nullable=False)
    day_of_month = Column(String, default='*', nullable=False)
    month_of_year = Column(String, default='*', nullable=False)

    @property
    def schedule(self):
        return celery.schedules.crontab(minute=self.minute,
                                        hour=self.hour,
                                        day_of_week=self.day_of_week,
                                        day_of_month=self.day_of_month,
                                        month_of_year=self.month_of_year)


class PeriodicTask(Model):
    __tablename__ = "periodic_task"

    id = Column(Integer, primary_key=True)
    uuid = Column('uuid', String, nullable=False, unique=True, default=gen_uuid)

    _role = Column("role", String, default=TaskRole.INITIALIZER.value)
    name = Column(String, unique=True)
    task = Column(String, nullable=False)
    _args = Column("args", Text)  # list
    _kwargs = Column("kwargs", Text)  # dict
    _options = Column("options", Text)  # dict

    initializer_task_id = Column(Integer, ForeignKey('periodic_task.id'))
    initializer = relationship("PeriodicTask", foreign_keys=[initializer_task_id], remote_side=id,
                               backref=backref('chord_tasks'))

    header_task_id = Column(Integer, ForeignKey('periodic_task.id'))
    header = relationship("PeriodicTask", foreign_keys=[header_task_id], remote_side=id,
                          backref=backref('callback_task', uselist=False))

    @property
    def options(self):
        if self._options:
            ops = json.loads(self._options)
            if isinstance(ops, dict):
                return ops
        return dict()

    @options.setter
    def options(self, value):
        if isinstance(value, str):
            value = json.loads(value)
        if isinstance(value, dict):
            self._options = json.dumps(value)

    @property
    def queue(self):
        if self.options:
            q = self.options.get("queue", None)
            if isinstance(q, str):
                return q
        return None

    @queue.setter
    def queue(self, value):
        value = str(value)
        options = self.options
        options["queue"] = value
        self.options = options

    @property
    def exchange(self):
        if self.options:
            ex = self.options.get("exchange", None)
            if isinstance(ex, str):
                return ex
        return None

    @exchange.setter
    def exchange(self, value):
        value = str(value)
        options = self.options
        options["exchange"] = value
        self.options = options

    @property
    def routing_key(self):
        if self.options:
            rt = self.options.get("routing_key", None)
            if isinstance(rt, str):
                return rt
        return None

    @routing_key.setter
    def routing_key(self, value):
        value = str(value)
        options = self.options
        options["routing_key"] = value
        self.options = options

    @property
    def soft_time_limit(self):
        if self.options:
            tlm = self.options.get("soft_time_limit", None)
            if isinstance(tlm, int):
                return tlm
        return None

    @soft_time_limit.setter
    def soft_time_limit(self, value):
        value = int(value)
        options = self.options
        options["soft_time_limit"] = value
        self.options = options

    expires = Column(DateTime)
    start_after = Column(DateTime)
    enabled = Column(Boolean, default=False)

    last_run_at = Column(DateTime)

    _total_run_count = Column("total_run_count", Integer, default=0)
    _max_run_count = Column("max_run_count", Integer, default=0)

    date_changed = Column(DateTime)
    description = Column(String)

    run_immediately = Column(Boolean)

    interval_id = Column(Integer, ForeignKey('interval.id'))
    interval = relationship("Interval", backref=backref('task', uselist=False))

    crontab_id = Column(Integer, ForeignKey('crontab.id'))
    crontab = relationship("Crontab", backref=backref('task', uselist=False))

    no_changes = False

    @property
    def args(self):
        if self._args:
            ret = json.loads(self._args)
            if isinstance(ret, list):
                return ret
        return list()

    @args.setter
    def args(self, value):
        if isinstance(value, str):
            value = json.loads(str)
        if isinstance(value, list):
            self._args = json.dumps(value)
        else:
            raise ValueError("args should be type of list")

    @property
    def kwargs(self):
        real_kwargs = dict()
        if self._kwargs:
            real_kwargs = json.loads(self._kwargs)

        if self._role in [TaskRole.CHORDS.value, TaskRole.CALLBACK.value]:
            return real_kwargs

        elif self._role == TaskRole.INITIALIZER.value:
            chords = []
            callback = None
            for task in self.chord_tasks:
                chords.append(task.to_json())
            if self.callback_task:
                callback = self.callback_task.to_json()
            ret = {"chords": chords, "callback": callback, "kwargs": real_kwargs}
            return ret
        return dict()

    @kwargs.setter
    def kwargs(self, value):
        if isinstance(value, str):
            value = json.loads(str)
        if isinstance(value, dict):
            self._kwargs = json.dumps(value)
        else:
            raise ValueError("kwargs should be type of dict")

    @property
    def total_run_count(self):
        return self._total_run_count

    @total_run_count.setter
    def total_run_count(self, value):
        self._total_run_count = max(value, 0)

    @property
    def max_run_count(self):
        return self._max_run_count

    @max_run_count.setter
    def max_run_count(self, value):
        self._max_run_count = max(value, 0)

    @property
    def schedule(self):
        if self.interval:
            return self.interval.schedule
        elif self.crontab:
            return self.crontab.schedule
        else:
            raise Exception("must define interval or crontab schedule")

    def to_json(self):
        ret = dict()
        ret["name"] = self.name
        ret["task"] = self.task
        ret["args"] = self.args
        ret["kwargs"] = self.kwargs
        return ret
