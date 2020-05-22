import pytest


@pytest.fixture(scope='session')
def app():
    from fleeter import create_app
    app = create_app('config.TestingConfig')
    context = app.app_context()
    context.push()
    yield app
    context.pop()


@pytest.fixture(scope='session')
def db(app):
    from fleeter import db
    db.init_app(app)

    return db


@pytest.fixture(scope='function')
def session(db):
    db.create_all()

    yield db.session

    # Explicitly close DB session
    db.session.close()
    db.drop_all()
