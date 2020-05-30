import json
import pytest
import requests
from fleeter.auth import AUTH0_DOMAIN, API_AUDIENCE
from fleeter.models import Fleet, Follow, User


@pytest.fixture(scope='module')
def client(app):
    return app.test_client()


@pytest.fixture(scope='module')
def user_client(app):
    url = f'https://{AUTH0_DOMAIN}/oauth/token'
    data = {'client_id': app.config['USER_CLIENT_ID'],
            'client_secret': app.config['USER_CLIENT_SECRET'],
            'audience': API_AUDIENCE, 'grant_type': 'client_credentials'}
    r = requests.post(url, json=data)
    user_token = r.json()['access_token']
    uc = app.test_client()
    uc.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {user_token}'
    return uc


@pytest.fixture(scope='module')
def mod_client(app):
    url = f'https://{AUTH0_DOMAIN}/oauth/token'
    data = {'client_id': app.config['MOD_CLIENT_ID'],
            'client_secret': app.config['MOD_CLIENT_SECRET'],
            'audience': API_AUDIENCE, 'grant_type': 'client_credentials'}
    r = requests.post(url, json=data)
    mod_token = r.json()['access_token']
    mc = app.test_client()
    mc.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {mod_token}'
    return mc


class TestGetUserFleets:

    url = '/api/users/4/fleets'  # Trevor

    def test_get_user_fleets(self, client, app):
        res = client.get(self.url)
        data = json.loads(res.data)

        assert res.status_code == 200
        assert data['success']
        assert data['total_fleets'] == 5
        assert data['total_following'] == 1
        assert data['total_followers'] == 1
        assert len(data['fleets']) <= app.config['FLEETS_PER_PAGE']

    def test_404_user_not_exist(self, client):
        res = client.get('/api/users/10/fleets')
        assert res.status_code == 404

    def test_422_non_positive_page_args(self, client):
        res1 = client.get(self.url + '?page=0')
        assert res1.status_code == 422

        res2 = client.get(self.url + '?per_page=0')
        assert res2.status_code == 422

    def test_404_page_out_of_range(self, client):
        res = client.get(self.url + '?page=20')
        assert res.status_code == 404


class TestGetUserFollowing:

    url = '/api/users/3/following'  # Franklin

    def test_401_unauthorized(self, client):
        res = client.get(self.url)
        assert res.status_code == 401
        assert json.loads(res.data)['code'] == 'authorization_header_missing'

    def test_get_user_following(self, user_client, app):
        res = user_client.get(self.url)
        data = json.loads(res.data)

        assert res.status_code == 200
        assert data['success']
        assert data['total_fleets'] == 4
        assert data['total_following'] == 1
        assert data['total_followers'] == 1
        assert len(data['following']) <= app.config['USERS_PER_PAGE']

    def test_404_user_not_exist(self, user_client):
        res = user_client.get('/api/users/10/following')
        assert res.status_code == 404

    def test_422_non_positive_page_args(self, user_client):
        res1 = user_client.get(self.url + '?page=-1')
        assert res1.status_code == 422

        res2 = user_client.get(self.url + '?per_page=0')
        assert res2.status_code == 422

    def test_404_page_out_of_range(self, user_client):
        res = user_client.get(self.url + '?page=10')
        assert res.status_code == 404


class TestGetUserFollowers:

    url = '/api/users/2/followers'  # Michael

    def test_401_unauthorized(self, client):
        res = client.get(self.url)
        assert res.status_code == 401
        assert json.loads(res.data)['code'] == 'authorization_header_missing'

    def test_get_user_followers(self, user_client, app):
        res = user_client.get(self.url)
        data = json.loads(res.data)

        assert res.status_code == 200
        assert data['success']
        assert data['total_fleets'] == 7
        assert data['total_following'] == 1
        assert data['total_followers'] == 3
        assert len(data['followers']) <= app.config['USERS_PER_PAGE']

    def test_404_user_not_exist(self, user_client):
        res = user_client.get('/api/users/10/followers')
        assert res.status_code == 404

    def test_422_non_positive_page_args(self, user_client):
        res1 = user_client.get(self.url + '?page=0')
        assert res1.status_code == 422

        res2 = user_client.get(self.url + '?per_page=-5')
        assert res2.status_code == 422

    def test_404_page_out_of_range(self, user_client):
        res = user_client.get(self.url + '?page=10')
        assert res.status_code == 404


class TestGetNewsFeed:

    url = '/api/fleets/newsfeed'

    def test_401_unauthorized(self, client):
        res = client.get(self.url)
        assert res.status_code == 401
        assert json.loads(res.data)['code'] == 'authorization_header_missing'

    def test_403_moderator(self, mod_client):
        res = mod_client.get(self.url)
        assert res.status_code == 403
        assert json.loads(res.data)['code'] == 'forbidden'

    def test_get_newsfeed(self, user_client, app):
        res = user_client.get(self.url)
        data = json.loads(res.data)

        assert res.status_code == 200
        assert data['success']
        assert data['total_fleets'] == 1
        assert data['total_following'] == 2
        assert data['total_followers'] == 0
        assert data['newsfeed_length'] == 13
        assert len(data['newsfeed']) <= app.config['FLEETS_PER_PAGE']

    def test_422_non_positive_page_args(self, user_client):
        res1 = user_client.get(self.url + '?page=-1')
        assert res1.status_code == 422

        res2 = user_client.get(self.url + '?per_page=-5')
        assert res2.status_code == 422

    def test_404_page_out_of_range(self, user_client):
        res = user_client.get(self.url + '?page=20')
        assert res.status_code == 404


class TestPostFleet:

    url = '/api/fleets'

    def test_401_unauthorized(self, client):
        res = client.post(self.url)
        assert res.status_code == 401
        assert json.loads(res.data)['code'] == 'authorization_header_missing'

    def test_403_moderator(self, mod_client):
        res = mod_client.post(self.url)
        assert res.status_code == 403
        assert json.loads(res.data)['code'] == 'forbidden'

    def test_post_fleet(self, user_client):
        res = user_client.post(self.url, json={'post': 'Fame or Shame'})
        data = json.loads(res.data)
        fleet = Fleet.query.get(data['id'])
        assert res.status_code == 200
        assert data['success']
        assert fleet.post == 'Fame or Shame'

    def test_400_no_post_arg(self, user_client):
        res = user_client.post(self.url, json={'fleet': 'Fame or Shame'})
        assert res.status_code == 400

    def test_422_empty_post(self, user_client):
        post_res = user_client.post(self.url, json={'post': ''})
        assert post_res.status_code == 422


class TestPatchFleet:

    url = '/api/fleets/17'

    def test_401_unauthorized(self, client):
        res = client.patch(self.url)
        assert res.status_code == 401
        assert json.loads(res.data)['code'] == 'authorization_header_missing'

    def test_403_moderator(self, mod_client):
        res = mod_client.patch(self.url)
        assert res.status_code == 403
        assert json.loads(res.data)['code'] == 'forbidden'

    def test_403_not_owner(self, user_client):
        res = user_client.patch('/api/fleets/1',
                                json={'post': 'welcome to Los Santos'})
        assert res.status_code == 403

    def test_patch_fleet(self, user_client):
        res = user_client.patch(self.url, json={'post': 'Fame or Shame'})
        data = json.loads(res.data)
        fleet = Fleet.query.get(17)
        assert res.status_code == 200
        assert data['success']
        assert data['id'] == 17
        assert fleet.post == 'Fame or Shame'

    def test_404_fleet_not_exist(self, user_client):
        res = user_client.patch('/api/fleets/100',
                                json={'post': 'The Big Score'})
        assert res.status_code == 404

    def test_400_no_post_arg(self, user_client):
        res = user_client.patch(self.url, json={'fleet': 'Fame or Shame'})
        assert res.status_code == 400

    def test_422_empty_post(self, user_client):
        res = user_client.patch(self.url, json={'post': ''})
        assert res.status_code == 422


class TestDeleteFleet:

    url = '/api/fleets/17'

    def test_401_unauthorized(self, client):
        res = client.delete(self.url)
        assert res.status_code == 401
        assert json.loads(res.data)['code'] == 'authorization_header_missing'

    def test_403_neither_owner_nor_moderator(self, user_client):
        res = user_client.delete('/api/fleets/1')
        assert res.status_code == 403

    def test_delete_fleet_as_owner(self, user_client):
        res = user_client.delete(self.url)
        data = json.loads(res.data)
        fleet = Fleet.query.get(17)
        assert res.status_code == 200
        assert data['success']
        assert data['id'] == 17
        assert fleet is None

    def test_delete_fleet_as_moderator(self, mod_client):
        res = mod_client.delete('/api/fleets/1')
        data = json.loads(res.data)
        fleet = Fleet.query.get(1)
        assert res.status_code == 200
        assert data['success']
        assert data['id'] == 1
        assert fleet is None

    def test_404_fleet_not_exist(self, user_client):
        res = user_client.delete('/api/fleets/100')
        assert res.status_code == 404


class TestFollow:

    url = '/api/follows/3'

    def test_401_unauthorized(self, client):
        res = client.post(self.url)
        assert res.status_code == 401
        assert json.loads(res.data)['code'] == 'authorization_header_missing'

    def test_403_moderator(self, mod_client):
        res = mod_client.post(self.url)
        assert res.status_code == 403
        assert json.loads(res.data)['code'] == 'forbidden'

    def test_follow(self, user_client):
        res = user_client.post(self.url)
        data = json.loads(res.data)
        follow = Follow.query.filter_by(follower_id=1,
                                        followee_id=3).one_or_none()
        assert res.status_code == 200
        assert data['success']
        assert data['id'] == 3
        assert follow is not None

    def test_404_followee_not_exist(self, user_client):
        res = user_client.post('/api/follows/10')
        assert res.status_code == 404

    def test_422_follow_self(self, user_client):
        res = user_client.post('/api/follows/1')
        assert res.status_code == 422


class TestUnfollow:

    url = '/api/follows/2'

    def test_401_unauthorized(self, client):
        res = client.delete(self.url)
        assert res.status_code == 401
        assert json.loads(res.data)['code'] == 'authorization_header_missing'

    def test_403_moderator(self, mod_client):
        res = mod_client.delete(self.url)
        assert res.status_code == 403
        assert json.loads(res.data)['code'] == 'forbidden'

    def test_unfollow(self, user_client):
        res = user_client.delete(self.url)
        data = json.loads(res.data)
        follow = Follow.query.filter_by(follower_id=1,
                                        followee_id=2).one_or_none()
        assert res.status_code == 200
        assert data['success']
        assert data['id'] == 2
        assert follow is None

    def test_404_followee_not_exist(self, user_client):
        res = user_client.delete('/api/follows/10')
        assert res.status_code == 404

    def test_422_unfollow_self(self, user_client):
        res = user_client.delete('/api/follows/1')
        assert res.status_code == 422


class TestDeleteUser:

    url = '/api/users/4'

    def test_401_unauthorized(self, client):
        res = client.delete(self.url)
        assert res.status_code == 401
        assert json.loads(res.data)['code'] == 'authorization_header_missing'

    def test_403_user(self, user_client):
        res = user_client.delete(self.url)
        assert res.status_code == 403
        assert json.loads(res.data)['code'] == 'forbidden'

    def test_delete_user(self, mod_client):
        res = mod_client.delete(self.url)
        data = json.loads(res.data)
        user = User.query.get(4)
        assert res.status_code == 200
        assert data['success']
        assert data['id'] == 4
        assert user is None

    def test_404_user_not_exist(self, mod_client):
        res = mod_client.delete('/api/users/10')
        assert res.status_code == 404
