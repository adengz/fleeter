from fleeter.models import User, Fleet


def test_follow(session):
    franklin = User.query.filter_by(username='Franklin Clinton').first()
    lamar = User.query.filter_by(username='Lamar Davis').first()
    assert lamar not in franklin.following.all()
    assert franklin not in lamar.followers.all()
    franklin.follow(lamar)
    assert lamar in franklin.following.all()
    assert franklin in lamar.followers.all()

    michael = User.query.filter_by(username='Michael De Santa').first()
    jimmy = User.query.filter_by(username='Jimmy De Santa').first()
    assert jimmy not in michael.following.all()
    assert michael not in jimmy.followers.all()
    michael.follow(jimmy)
    assert jimmy in michael.following.all()
    assert michael in jimmy.followers.all()


def test_unfollow(session):
    lamar = User.query.filter_by(username='Lamar Davis').first()
    stretch = User.query.filter_by(username='Harold Stretch Joseph').first()
    assert lamar.is_following(stretch)
    lamar.unfollow(stretch)
    assert stretch not in lamar.following.all()
    assert lamar not in stretch.followers.all()

    kyle = User.query.filter_by(username='Kyle Chavis').first()
    amanda = User.query.filter_by(username='Amanda De Santa').first()
    assert kyle.is_following(amanda)
    kyle.unfollow(amanda)
    assert amanda not in kyle.following.all()
    assert kyle not in amanda.followers.all()


def test_user_get_own_fleets(session):
    devin = User.query.filter_by(username='Devin Weston').first()
    devin_fleets = devin.get_fleets(following=False).all()
    assert len(devin_fleets) == 5
    assert set([f.user for f in devin_fleets]) == {devin}
    assert 'Meltdown' in devin_fleets[0].post
    assert sorted(devin_fleets, key=lambda f: f.created_at, reverse=True) \
           == devin_fleets

    lester = User.query.filter_by(username='Lester Crest').first()
    lester_fleets = lester.get_fleets(following=False).all()
    assert len(lester_fleets) == 9
    assert set([f.user for f in lester_fleets]) == {lester}
    assert 'Lifeinvader' in lester_fleets[-1].post
    assert sorted(lester_fleets, key=lambda f: f.created_at, reverse=True) \
           == lester_fleets

    wade = User.query.filter_by(username='Wade Herbert').first()
    wade_fleets = wade.get_fleets(following=False).all()
    assert len(wade_fleets) == 2
    assert set([f.user for f in wade_fleets]) == {wade}
    assert 'Los Santos' in wade_fleets[-1].post
    assert sorted(wade_fleets, key=lambda f: f.created_at, reverse=True) \
           == wade_fleets


def test_user_get_newsfeed(session):
    tanisha = User.query.filter_by(username='Tanisha Jackson').first()
    tanisha_newsfeed = tanisha.get_fleets(following=True).all()
    all_tanisha_fleets = []
    for user in [tanisha] + tanisha.following.all():
        all_tanisha_fleets.extend(Fleet.query.filter_by(user_id=user.id))
    all_tanisha_fleets.sort(key=lambda f: f.created_at, reverse=True)
    assert all_tanisha_fleets == tanisha_newsfeed

    kyle = User.query.filter_by(username='Kyle Chavis').first()
    kyle_newsfeed = kyle.get_fleets(following=True).all()
    all_kyle_fleets = []
    for user in [kyle] + kyle.following.all():
        all_kyle_fleets.extend(Fleet.query.filter_by(user_id=user.id))
    all_kyle_fleets.sort(key=lambda f: f.created_at, reverse=True)
    assert all_kyle_fleets == kyle_newsfeed
