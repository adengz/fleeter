import pytest
import csv
from pathlib import Path
from datetime import datetime, timedelta


DATA_ROOT = Path('../data')
CSV_FILE = 'gtav_events.csv'


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


# Initiate test db state for every test
@pytest.fixture(scope='function', autouse=True)
def users(session, app):
    from fleeter.models import User, Fleet, Follow
    users = {}
    for name in ['player', 'Michael', 'Franklin', 'Trevor']:
        users[name] = User(username=name)
    users['player'].auth0_id = app.config['USER_CLIENT_ID'] + '@clients'
    session.add_all(users.values())
    session.commit()

    now = datetime.now()
    fleets, follows = [], []
    with open(DATA_ROOT / CSV_FILE) as f:
        reader = csv.reader(f)
        for u, event in reader:
            user = users[u]
            if event.startswith('follow'):
                followee = users[event.split()[-1]]
                follows.append(Follow(follower_id=user.id,
                                      followee_id=followee.id,
                                      created_at=now))
            else:
                fleets.append(Fleet(post=event, user=user, created_at=now))
            now += timedelta(seconds=1)
    fleets.append(Fleet(post='Hola, Los Santos', user=users['player']))
    session.add_all(fleets)
    session.add_all(follows)
    session.commit()

    return users
