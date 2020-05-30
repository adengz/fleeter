import json
import pytest
import requests
from fleeter.auth import AUTH0_DOMAIN, API_AUDIENCE
from fleeter.models import Fleet


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


class TestAuth:

    def test_get_user_follow(self, user_client, mod_client):
        res_following = user_client.get('/api/users/1/following')
        assert res_following.status_code == 200

        res_followers = user_client.get('/api/users/2/followers')
        assert res_followers.status_code == 200

    def test_get_newsfeed(self, user_client):
        res = user_client.get('/api/fleets/newsfeed')
        assert res.status_code == 200

    def test_post_fleet(self, user_client):
        res = user_client.post('/api/fleets', json={'post': 'Fame or Shame'})
        assert res.status_code == 200

    def test_patch_fleet(self, user_client):
        res = user_client.patch('/api/fleets/17',
                                json={'post': 'Fame or Shame'})
        assert res.status_code == 200

    def test_delete_fleet_owner(self, user_client):
        res = user_client.delete('/api/fleets/17')
        assert res.status_code == 200

    def test_delete_fleet_mod(self, mod_client):
        res = mod_client.delete('/api/fleets/1')
        assert res.status_code == 200

    def test_403_patch_delete_fleet_not_owner(self, user_client):
        patch_res = user_client.patch('/api/fleets/1',
                                      json={'post': 'welcome to Los Santos'})
        assert patch_res.status_code == 403

        delete_res = user_client.delete('/api/fleets/1')
        assert delete_res.status_code == 403

    def test_401_endpoints_require_auth_unauthed(self, client):
        code = 'authorization_header_missing'

        following_res = client.get('/api/users/1/following')
        assert following_res.status_code == 401
        assert json.loads(following_res.data)['code'] == code

        followers_res = client.get('/api/users/2/followers')
        assert followers_res.status_code == 401
        assert json.loads(followers_res.data)['code'] == code

        newsfeed_res = client.get('/api/fleets/newsfeed')
        assert newsfeed_res.status_code == 401
        assert json.loads(newsfeed_res.data)['code'] == code

        post_fleet_res = client.post('/api/fleets',
                                     json={'post': 'Fame or Shame'})
        assert post_fleet_res.status_code == 401

        patch_fleet_res = client.patch('/api/fleets/17',
                                       json={'post': 'Fame or Shame'})
        assert patch_fleet_res.status_code == 401

        delete_fleet_res = client.delete('/api/fleets/17')
        assert delete_fleet_res.status_code == 401

    def test_403_user_endpoints_mod(self, mod_client):
        code = 'forbidden'

        newsfeed_res = mod_client.get('/api/fleets/newsfeed')
        assert newsfeed_res.status_code == 403
        assert json.loads(newsfeed_res.data)['code'] == code

        post_fleet_res = mod_client.post('/api/fleets',
                                         json={'post': 'Fame or Shame'})
        assert post_fleet_res.status_code == 403

        patch_fleet_res = mod_client.patch('/api/fleets/17',
                                           json={'post': 'Fame or Shame'})
        assert patch_fleet_res.status_code == 403


class TestEndpoints:

    def test_get_user_fleets(self, client, app, users):
        res = client.get(f'/api/users/{users["Trevor"].id}/fleets')
        data = json.loads(res.data)

        assert res.status_code == 200
        assert data['success']
        assert data['total_fleets'] == 5
        assert data['total_following'] == 1
        assert data['total_followers'] == 1
        assert len(data['fleets']) <= app.config['FLEETS_PER_PAGE']

    def test_get_user_following(self, user_client, app, users):
        res = user_client.get(f'/api/users/{users["Franklin"].id}/following')
        data = json.loads(res.data)

        assert res.status_code == 200
        assert data['success']
        assert data['total_fleets'] == 4
        assert data['total_following'] == 1
        assert data['total_followers'] == 1
        assert len(data['following']) <= app.config['USERS_PER_PAGE']

    def test_get_user_followers(self, user_client, app, users):
        res = user_client.get(f'/api/users/{users["Michael"].id}/followers')
        data = json.loads(res.data)

        assert res.status_code == 200
        assert data['success']
        assert data['total_fleets'] == 7
        assert data['total_following'] == 1
        assert data['total_followers'] == 3
        assert len(data['followers']) <= app.config['USERS_PER_PAGE']

    def test_get_newsfeed(self, user_client, app):
        res = user_client.get('/api/fleets/newsfeed')
        data = json.loads(res.data)

        assert res.status_code == 200
        assert data['success']
        assert data['total_fleets'] == 1
        assert data['total_following'] == 2
        assert data['total_followers'] == 0
        assert data['newsfeed_length'] == 13
        assert len(data['newsfeed']) <= app.config['FLEETS_PER_PAGE']

    def test_404_get_user_items_user_not_found(self, user_client):
        fleets_res = user_client.get('/api/users/100/fleets')
        assert fleets_res.status_code == 404
        assert not json.loads(fleets_res.data)['success']

        following_res = user_client.get('/api/users/100/following')
        assert following_res.status_code == 404
        assert not json.loads(following_res.data)['success']

        followers_res = user_client.get('/api/users/100/followers')
        assert followers_res.status_code == 404
        assert not json.loads(followers_res.data)['success']

    def test_422_get_user_items_non_positive_page_args(self, user_client):
        fleets_res = user_client.get('/api/users/2/fleets?page=0')
        assert fleets_res.status_code == 422
        assert not json.loads(fleets_res.data)['success']

        following_res = user_client.get('/api/users/3/following?per_page=0')
        assert following_res.status_code == 422
        assert not json.loads(following_res.data)['success']

        followers_res = user_client.get('/api/users/4/followers?page=-1')
        assert followers_res.status_code == 422
        assert not json.loads(followers_res.data)['success']

        newsfeed_res = user_client.get('/api/fleets/newsfeed?per_page=-5')
        assert newsfeed_res.status_code == 422
        assert not json.loads(newsfeed_res.data)['success']

    def test_404_get_user_items_page_out_of_range(self, user_client, users):
        fleets_url = f'/api/users/{users["Trevor"].id}/fleets'
        fleets_res = user_client.get(fleets_url + '?page=10')
        assert fleets_res.status_code == 404
        assert not json.loads(fleets_res.data)['success']

        following_url = f'/api/users/{users["Franklin"].id}/following'
        following_res = user_client.get(following_url + '?page=5')
        assert following_res.status_code == 404
        assert not json.loads(following_res.data)['success']

        followers_url = f'/api/users/{users["Michael"].id}/followers'
        followers_res = user_client.get(followers_url + '?page=5')
        assert followers_res.status_code == 404
        assert not json.loads(followers_res.data)['success']

        newsfeed_res = user_client.get('/api/fleets/newsfeed?page=20')
        assert newsfeed_res.status_code == 404
        assert not json.loads(newsfeed_res.data)['success']

    def test_post_fleet(self, user_client):
        res = user_client.post('/api/fleets', json={'post': 'Fame or Shame'})
        data = json.loads(res.data)
        fleet = Fleet.query.get(data['id'])
        assert res.status_code == 200
        assert data['success']
        assert fleet.post == 'Fame or Shame'

    def test_patch_fleet(self, user_client):
        res = user_client.patch('/api/fleets/17',
                                json={'post': 'Fame or Shame'})
        data = json.loads(res.data)
        fleet = Fleet.query.get(17)
        assert res.status_code == 200
        assert data['success']
        assert data['id'] == 17
        assert fleet.post == 'Fame or Shame'

    def test_delete_fleet(self, user_client):
        res = user_client.delete('/api/fleets/17')
        data = json.loads(res.data)
        fleet = Fleet.query.get(17)
        assert res.status_code == 200
        assert data['success']
        assert data['id'] == 17
        assert fleet is None

    def test_404_patch_delete_fleet_not_exist(self, user_client):
        patch_res = user_client.patch('/api/fleets/100',
                                      json={'post': 'The Big Score'})
        assert patch_res.status_code == 404
        assert not json.loads(patch_res.data)['success']

        delete_res = user_client.delete('/api/fleets/100')
        assert delete_res.status_code == 404
        assert not json.loads(delete_res.data)['success']

    def test_400_post_fleet_no_post_arg(self, user_client):
        res = user_client.post('/api/fleets',
                               json={'fleet': 'Fame or Shame'})
        assert res.status_code == 400
        assert not json.loads(res.data)['success']

    def test_400_patch_fleet_no_post_arg(self, user_client):
        res = user_client.patch('/api/fleets/17',
                                json={'fleet': 'Fame or Shame'})
        assert res.status_code == 400
        assert not json.loads(res.data)['success']

    def test_422_post_patch_fleet_empty_post(self, user_client):
        post_res = user_client.post('/api/fleets', json={'post': ''})
        assert post_res.status_code == 422
        assert not json.loads(post_res.data)['success']

        patch_res = user_client.patch('/api/fleets/17', json={'post': ''})
        assert patch_res.status_code == 422
        assert not json.loads(patch_res.data)['success']
