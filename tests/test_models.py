from datetime import datetime, timedelta
from fleeter.models import User, Fleet


def test_follow(session):
    user1 = User(username='john')
    user2 = User(username='jane')
    session.add_all([user1, user2])
    session.commit()

    assert user1.following.all() == []
    assert user2.followers.all() == []

    user1.follow(user2)
    assert user2 in user1.following.all()
    assert user1 in user2.followers.all()


def test_unfollow(session):
    user1 = User(username='john')
    user2 = User(username='jane')
    session.add_all([user1, user2])
    session.commit()
    user1.following.append(user2)
    session.commit()

    assert user1.is_following(user2)

    user1.unfollow(user2)
    assert user2 not in user1.following.all()
    assert user1 not in user2.followers.all()


def test_user_get_own_fleets(session):
    user = User(username='john')
    now = datetime.now()
    f1 = Fleet(post='first fleet', user=user,
               created_at=(now + timedelta(seconds=1)))
    f2 = Fleet(post='second fleet', user=user,
               created_at=(now + timedelta(seconds=2)))
    f3 = Fleet(post='third fleet', user=user,
               created_at=(now + timedelta(seconds=3)))
    session.add(user)
    session.commit()

    own_fleets = user.get_fleets(following=False)
    assert own_fleets.all() == [f3, f2, f1]


def test_user_get_newsfeed(session):
    users = {}
    for name in ['mike', 'susan', 'david', 'karen']:
        users[name] = User(username=name)
    session.add_all(users.values())
    session.commit()
    users['susan'].following.append(users['mike'])
    users['susan'].following.append(users['karen'])
    users['david'].following.append(users['mike'])
    users['karen'].following.append(users['mike'])
    users['karen'].following.append(users['david'])
    users['karen'].following.append(users['susan'])
    now = datetime.now()
    f1 = Fleet(post='fleet by mike', user=users['mike'],
               created_at=(now + timedelta(seconds=1)))
    f2 = Fleet(post='fleet by david', user=users['david'],
               created_at=(now + timedelta(seconds=2)))
    f3 = Fleet(post='fleet by karen', user=users['karen'],
               created_at=(now + timedelta(seconds=3)))
    f4 = Fleet(post='fleet by susan', user=users['susan'],
               created_at=(now + timedelta(seconds=4)))
    session.commit()

    assert users['mike'].get_fleets(following=True).all() == [f1]
    assert users['susan'].get_fleets(following=True).all() == [f4, f3, f1]
    assert users['david'].get_fleets(following=True).all() == [f2, f1]
    assert users['karen'].get_fleets(following=True).all() == [f4, f3, f2, f1]
