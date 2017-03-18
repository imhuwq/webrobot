import os

SECRET_COOKIE = ')5T1~dLb~isIUrta2&_Cu90xzKmx!V6T2A^eI~z#33ZlPTm6SaFo(IUSBVU6'

email = {
    'host': '',
    'port': 465,
    'user': '',
    'password': ''
}

SETTINGS = {
    "cookie_secret": SECRET_COOKIE,
    "xsrf_cookies": True,
    'login_url': '/login',
    'email': email
}

DB_CONFIG = {
    'username': 'twinado',
    'password': 'twinado',
    'database': 'twinado',
    'host': 'localhost',
    'port': 5432
}

DB_URI = 'postgresql+psycopg2://%s:%s@%s:%d/%s' % (DB_CONFIG.get('username'),
                                                   DB_CONFIG.get('password'),
                                                   DB_CONFIG.get('host'),
                                                   DB_CONFIG.get('port'),
                                                   DB_CONFIG.get('database'))

CONFIG_DIR = os.path.abspath(os.path.dirname(__file__))
SERVER_DIR = os.path.abspath(os.path.join(CONFIG_DIR, '../'))
REPO_DIR = os.path.abspath(os.path.join(SERVER_DIR, '../'))

TEST_DB_URI = 'sqlite:///' + os.path.join(REPO_DIR, 'test.sqlite')
DEVE_DB_URI = 'sqlite:///' + os.path.join(REPO_DIR, 'deve.sqlite')
