import os


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLEETS_PER_PAGE = 10
    USERS_PER_PAGE = 2


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ['TEST_DATABASE_URL']
    # Used for getting access jwt for testing
    USER_CLIENT_ID = '1cR4ZOIFhQ2218VYQ0L5Vdc9z7LRwpz2'
    USER_CLIENT_SECRET = 'lHPfxJDcT6HynlLVUQ-SfYFhcTmPgY_9AxlCNQy88qm5KwGSMrc-X9DEqlYpJ_8M'
    MOD_CLIENT_ID = 'LSLFxDjNTCsXrtcI7RAIzc8RNsv0L4Al'
    MOD_CLIENT_SECRET = 'nLiIGEndblUCgIlj-dA7aj75i-9EM3YvsbDZs_hAmEa5C5fvVcKYa6S14URo1fPD'
