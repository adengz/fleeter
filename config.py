LOCAL_DB_CONN = 'localhost:5432'
DB_NAME = 'fleeter'
TEST_DB_NAME = 'fleeter_test'


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = f'postgres://{LOCAL_DB_CONN}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f'postgres://{LOCAL_DB_CONN}/{TEST_DB_NAME}'