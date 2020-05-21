from datetime import datetime, timedelta
import pytest
from fleeter import create_app, db
from fleeter.models import User, Fleet


@pytest.fixture
def db_test():
    app = create_app('config.TestingConfig')
    db.init_app(app)
    with app.app_context():
        db.create_all()

        yield db

        # Explicitly close DB session
        db.session.close()
        db.drop_all()


def test_user_get_own_fleets(db_test):
    user = User(username='john')
    now = datetime.now()
    f1 = Fleet(post='first fleet', user=user,
               created_at=(now + timedelta(seconds=1)))
    f2 = Fleet(post='second fleet', user=user,
               created_at=(now + timedelta(seconds=2)))
    f3 = Fleet(post='third fleet', user=user,
               created_at=(now + timedelta(seconds=3)))
    db_test.session.add(user)
    db_test.session.commit()

    newsfeed = user.get_fleets()
    assert newsfeed == [f3, f2, f1]