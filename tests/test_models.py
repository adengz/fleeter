from fleeter.models import User, Fleet


def test_user_to_dict(session):
    lamar = User.query.filter_by(username='Lamar Davis').first()
    lamar_dict = lamar.to_dict()
    assert lamar_dict['id'] == 3
    assert lamar_dict['username'] == 'Lamar Davis'
    assert lamar_dict['fleets'] == 6
    assert lamar_dict['following'] == 4
    assert lamar_dict['followers'] == 9

    jimmy = User.query.filter_by(username='Jimmy De Santa').first()
    jimmy_dict = jimmy.to_dict()
    assert jimmy_dict['id'] == 14
    assert jimmy_dict['username'] == 'Jimmy De Santa'
    assert jimmy_dict['fleets'] == 20
    assert jimmy_dict['following'] == 3
    assert jimmy_dict['followers'] == 3

    ron = User.query.filter_by(username='Ron Jakowski').first()
    ron_dict = ron.to_dict()
    assert ron_dict['id'] == 26
    assert ron_dict['username'] == 'Ron Jakowski'
    assert ron_dict['fleets'] == 0
    assert ron_dict['following'] == 1
    assert ron_dict['followers'] == 1


def test_user_follow(session):
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


def test_user_unfollow(session):
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


def test_fleet_to_dict(session):
    jewel_post = 'NO!!!! My favorite jewelry store got robbed!'
    jewel = Fleet.query.get(29)
    jewel_dict = jewel.to_dict()
    assert jewel_dict['id'] == 29
    assert jewel_dict['post'] == jewel_post
    assert jewel_dict['username'] == 'Amanda De Santa'

    ud_post = 'How the hell did the Union Depository get broken into? ' \
              'I thought it was supposed to be impenetrable! ' \
              'What\'s this going to do to the dollar?'
    ud = Fleet.query.get(134)
    ud_dict = ud.to_dict()
    assert ud_dict['id'] == 134
    assert ud_dict['post'] == ud_post
    assert ud_dict['username'] == 'Hayden Dubose'
