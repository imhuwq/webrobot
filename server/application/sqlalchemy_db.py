import uuid

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


class DataBaseURIError(BaseException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


Model = declarative_base()


class DataBase:
    def __init__(self):
        self.engine = None
        self.session = None
        self.Model = Model

    def init_app(self, app):
        if not app.db_uri:
            raise DataBaseURIError('Please specify your database URI')
        self.engine = create_engine(app.db_uri)
        self.session = scoped_session(sessionmaker(bind=self.engine))
        app.db = self

    def create_all(self):
        self.Model.metadata.create_all(self.engine)

    def drop_all(self):
        self.Model.metadata.drop_all(self.engine)


def gen_uuid():
    return uuid.uuid4().hex


class User(Model):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True)
    uuid = Column('uuid', String, nullable=False, unique=True, default=gen_uuid)
