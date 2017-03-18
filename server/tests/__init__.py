import os
import unittest

from server.application.tornado_config import SERVER_DIR


class UnitTest:
    def __init__(self):
        pass

    @staticmethod
    def run():
        start_dir = os.path.join(SERVER_DIR, 'tests/unit')
        tests = unittest.TestLoader().discover(start_dir, pattern='*.py')
        unittest.TextTestRunner(verbosity=2, failfast=True).run(tests)
