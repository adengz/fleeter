from datetime import datetime, timedelta
from fleeter.models import User, Fleet, Follow


def test_follow(session):
    user1 = User(username='john')
    user2 = User(username='jane')
    session.add_all([user1, user2])
    session.commit()

    assert user1.following.all() == []
    assert user2.followers.all() == []

    user1.follow(user2)
    assert user1.following.all() == [user2]
    assert user2.followers.all() == [user1]


def test_unfollow(session):
    user1 = User(username='john')
    user2 = User(username='jane')
    session.add_all([user1, user2])
    session.commit()
    follow = Follow(follower_id=user1.id, followee_id=user2.id)
    session.add(follow)
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
    me = User(username='me')
    my_fleet = Fleet(post='DO NOT TAKE THAT HELI Kobe', user=me,
                     created_at=datetime(2020, 1, 26, 9, 00, 00, 0))
    ariana = User(username='ArianaGrande')
    ariana_fleet = Fleet(post='sending love. be safe.', user=ariana,
                         created_at=datetime(2020, 3, 12, 15, 12, 00, 0))
    trump = User(username='realDonaldTrump')
    trump_fleet = Fleet(post='Despite the constant negative press covfefe',
                        user=trump,
                        created_at=datetime(2017, 5, 31, 0, 6, 00, 0))
    session.add_all([me, ariana, trump])
    session.commit()
    follow = Follow(follower_id=me.id, followee_id=ariana.id)
    session.add(follow)
    session.commit()

    news_feed = me.get_fleets(following=True)
    assert news_feed.all() == [ariana_fleet, my_fleet]
