import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


'''
This wonderful rollback-any-committed-transaction setup 
is fully credited to the following medium post
https://medium.com/@vittorio.camisa/agile-database-integration-tests-with-python-sqlalchemy-and-factory-boy-6824e8fe33a1
'''


Session = sessionmaker()


@pytest.fixture(scope='session')
def app():
    from fleeter import create_app
    app = create_app('config.TestingConfig')
    context = app.app_context()
    context.push()
    yield app
    context.pop()


@pytest.fixture(scope='session')
def name_to_id(app):
    from fleeter import db
    from fleeter.models import User
    db.init_app(app)
    return {u.username: u.id for u in User.query.all()}


@pytest.fixture(scope='session')
def connection(app):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    connection = engine.connect()
    yield connection
    connection.close()


@pytest.fixture(scope='function')
def session(connection):
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    # Explicitly close session
    session.close()
    # Rollback any transactions
    transaction.rollback()
