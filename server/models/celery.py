import json
import datetime
from enum import Enum

from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
import celery.schedules

from server.application import db
from server.utils import gen_uuid
from server.modules.celery.task import TaskTypes
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
    __tablename__ = "intervals"

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

    @classmethod
    def new_interval(cls, every, unit):
        interval = cls()
        interval.every = every
        interval.period = unit
        db.session.add(interval)
        db.session.flush()
        return interval


class Crontab(Model):
    __tablename__ = "crontabs"

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

    @classmethod
    def new_crontab(cls, minute, hour, day_of_week, day_of_month, month_of_year):
        crontab = cls()
        crontab.minute = minute
        crontab.hour = hour
        crontab.day_of_week = day_of_week
        crontab.day_of_month = day_of_month
        crontab.month_of_year = month_of_year
        db.session.add(crontab)
        db.session.flush()
        return crontab


class PeriodicTask(Model):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    uuid = Column('uuid', String, nullable=False, unique=True, default=gen_uuid)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", foreign_keys=[user_id], backref=backref('tasks'))

    _role = Column("role", String, default=TaskRole.INITIALIZER.value)
    name = Column(String, unique=True)
    _task = Column("task", String, nullable=False)
    enabled = Column(Boolean, default=False)

    _args = Column("args", Text)  # list
    _kwargs = Column("kwargs", Text)  # dict
    _options = Column("options", Text)  # dict

    initializer_task_id = Column(Integer, ForeignKey('tasks.id'))
    initializer = relationship("PeriodicTask", foreign_keys=[initializer_task_id], remote_side=id,
                               backref=backref('chord_tasks'))

    header_task_id = Column(Integer, ForeignKey('tasks.id'))
    header = relationship("PeriodicTask", foreign_keys=[header_task_id], remote_side=id,
                          backref=backref('callback_task', uselist=False))

    expires = Column(DateTime)
    start_after = Column(DateTime, default=datetime.datetime.utcnow)
    last_run_at = Column(DateTime)

    _total_run_count = Column("total_run_count", Integer, default=0)
    _max_run_count = Column("max_run_count", Integer, default=0)

    date_changed = Column(DateTime)
    description = Column(String)
    run_immediately = Column(Boolean, default=False)

    interval_id = Column(Integer, ForeignKey('intervals.id'))
    interval = relationship("Interval", backref=backref('task', uselist=False))

    crontab_id = Column(Integer, ForeignKey('crontabs.id'))
    crontab = relationship("Crontab", backref=backref('task', uselist=False))

    no_changes = False

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

    @property
    def role(self):
        return TaskRole(self._role)

    @role.setter
    def role(self, value):
        if not isinstance(value, TaskRole):
            value = TaskRole(value)
        self._role = value.value

    @property
    def task(self):
        return TaskTypes(self._task)

    @task.setter
    def task(self, value):
        if not isinstance(value, TaskTypes):
            value = TaskTypes(value)
        self._task = value.value

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

    @classmethod
    def new_init_task(cls, user, period):
        init = cls(user=user)
        init.role = TaskRole.INITIALIZER
        init.task = TaskTypes.TASK_INITIALIZER
        db.session.add(init)
        db.session.flush()

        method = period.get("method")
        if method == "interval":
            interval = Interval.new_interval(period.get("every"), period.get("unit"))
            init.interval = interval
        elif method == "crontab":
            crontab = Crontab.new_crontab(
                period.get("minute"),
                period.get("hour"),
                period.get("day_of_week"),
                period.get("day_of_month"),
                period.get("month_of_year"),
            )
            init.crontab = crontab
        db.session.flush()

        return init

    @classmethod
    def new_chord_task(cls, chord, init_task):
        task = cls()
        task.role = TaskRole.CHORDS
        task.task = chord.get("type")
        task.args = chord.get("args", [])
        task.kwargs = chord.get("kwargs")
        task.initializer = init_task
        db.session.add(task)
        db.session.flush()
        return task

    @classmethod
    def new_callback_task(cls, callback, init_task):
        task = cls()
        task.role = TaskRole.CALLBACK
        task.task = callback.get("type")
        task.args = callback.get("args", [])
        task.kwargs = callback.get("kwargs")
        task.header = init_task
        db.session.add(task)
        db.session.flush()
        return task
