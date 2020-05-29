LOCAL_DB_CONN = 'localhost:5432'
DB_NAME = 'fleeter'
TEST_DB_NAME = 'fleeter_test'


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = f'postgresql://{LOCAL_DB_CONN}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLEETS_PER_PAGE = 10
    USERS_PER_PAGE = 2


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f'postgresql://{LOCAL_DB_CONN}/{TEST_DB_NAME}'
    # Used for getting access jwt for testing
    USER_CLIENT_ID = '1cR4ZOIFhQ2218VYQ0L5Vdc9z7LRwpz2'
    USER_CLIENT_SECRET = 'lHPfxJDcT6HynlLVUQ-SfYFhcTmPgY_9AxlCNQy88qm5KwGSMrc-X9DEqlYpJ_8M'
    MOD_CLIENT_ID = 'LSLFxDjNTCsXrtcI7RAIzc8RNsv0L4Al'
    MOD_CLIENT_SECRET = 'nLiIGEndblUCgIlj-dA7aj75i-9EM3YvsbDZs_hAmEa5C5fvVcKYa6S14URo1fPD'
