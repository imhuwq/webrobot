from sqlalchemy.exc import IntegrityError

from server.models import User
from server.tests.unit import ModelTestBase


class UserModelTest(ModelTestBase):
    def test_user_create(self):
        user = User(name='john')
        self.db.session.add(user)
        self.db.session.commit()

        created = self.db.session.query(User).get(1)
        self.assertTrue(created is not None)
        self.assertTrue(created.name == 'john')
        self.assertTrue(created.uuid is not None)
        self.assertTrue(created == self.db.session.query(User).filter_by(name='john').first())

    def test_user_password(self):
        user = User(name='john', email='john@hu.com')
        password = 'apasswordshouldbeinvisible'
        user.set_password(password)
        self.db.session.add(user)
        self.db.session.commit()

        created = self.db.session.query(User).get(1)
        self.assertTrue(created.authenticate(password))
        self.assertFalse(created.authenticate('adf2434gdsfsfs'))

    def test_user_name_email_unique(self):
        user = User(name='john', email='john@hu.com')
        password = 'apasswordshouldbeinvisible'
        user.set_password(password)
        self.db.session.add(user)
        self.db.session.commit()

        with self.assertRaises(IntegrityError):
            user = User(name='john', email='john@huhuhu.com')
            password = 'apasswordshouldbeinvisible'
            user.set_password(password)
            self.db.session.add(user)
            self.db.session.commit()

        self.db.session.rollback()

        with self.assertRaises(IntegrityError):
            user = User(name='johasdn', email='john@hu.com')
            password = 'apasswordshouldbeinvisible'
            user.set_password(password)
            self.db.session.add(user)
            self.db.session.commit()
