from fleeter.models import Fleet, Follow


class TestUser:

    def test_to_dict(self, users):
        player_dict = users['player'].to_dict()
        assert player_dict['id'] == 1
        assert player_dict['username'] == 'player'
        assert player_dict['total_fleets'] == 0
        assert player_dict['total_following'] == 2
        assert player_dict['total_followers'] == 0
        assert 'auth0_id' not in player_dict

        franklin_dict = users['Franklin'].to_dict()
        assert franklin_dict['id'] == 3
        assert franklin_dict['username'] == 'Franklin'
        assert franklin_dict['total_fleets'] == 4
        assert franklin_dict['total_following'] == 1
        assert franklin_dict['total_followers'] == 1
        assert 'auth0_id' not in franklin_dict

    def test_fleets(self, users):
        trevor_fleets = [f.post for f in users['Trevor'].fleets.all()]
        assert trevor_fleets == ['Friends Reunited', 'Crystal Maze',
                                 'Trevor Philips Industries', 'Nervous Ron',
                                 'Mr. Philips']

    def test_following_followers(self, users):
        player_following = [u.username for u in
                            users['player'].following.all()]
        assert player_following == ['Michael', 'Trevor']

        michael_followers = [u.username for u in
                             users['Michael'].followers.all()]
        assert michael_followers == ['player', 'Trevor', 'Franklin']

    def test_newsfeed(self, users):
        franklin_newsfeed = [f.post for f in users['Franklin'].newsfeed.all()]
        fleets = users['Franklin'].fleets.all()
        fleets += users['Michael'].fleets.all()
        fleets.sort(key=lambda f: f.created_at, reverse=True)
        assert franklin_newsfeed == [f.post for f in fleets]

    def test_follow(self, users, session):
        michael = users['Michael']
        trevor = users['Trevor']
        query = Follow.query.filter_by(follower_id=michael.id,
                                       followee_id=trevor.id)

        assert trevor not in michael.following.all()
        assert michael not in trevor.followers.all()
        assert not michael.is_following(trevor)
        assert query.one_or_none() is None

        michael.follow(trevor)
        session.commit()
        assert trevor in michael.following.all()
        assert michael in trevor.followers.all()
        assert michael.is_following(trevor)
        assert query.one_or_none() is not None

    def test_unfollow(self, users, session):
        michael = users['Michael']
        trevor = users['Trevor']
        query = Follow.query.filter_by(follower_id=trevor.id,
                                       followee_id=michael.id)

        assert trevor in michael.followers.all()
        assert michael in trevor.following.all()
        assert trevor.is_following(michael)
        assert query.one_or_none() is not None

        trevor.unfollow(michael)
        session.commit()
        assert trevor not in michael.followers.all()
        assert michael not in trevor.following.all()
        assert not trevor.is_following(michael)
        assert query.one_or_none() is None


def test_fleet_to_dict():
    fleet1_dict = Fleet.query.get(11).to_dict()
    assert fleet1_dict['id'] == 11
    assert fleet1_dict['post'] == 'The Jewel Store Job'
    assert fleet1_dict['username'] == 'Michael'

    fleet2_dict = Fleet.query.get(15).to_dict()
    assert fleet2_dict['id'] == 15
    assert fleet2_dict['post'] == 'Crystal Maze'
    assert fleet2_dict['username'] == 'Trevor'
