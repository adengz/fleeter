import json
import pytest
import requests
from fleeter.auth import AUTH0_DOMAIN, API_AUDIENCE


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
        res1 = user_client.get('/api/users/1/following')
        assert res1.status_code == 200

        res2 = user_client.get('/api/users/1/followers')
        assert res2.status_code == 200

        res3 = mod_client.get('/api/users/2/following')
        assert res3.status_code == 200

        res4 = mod_client.get('/api/users/2/followers')
        assert res4.status_code == 200

    def test_get_newsfeed(self, user_client):
        res = user_client.get('/api/fleets/newsfeed')
        assert res.status_code == 200

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

    def test_403_user_endpoints_mod(self, mod_client):
        code = 'forbidden'

        newsfeed_res = mod_client.get('/api/fleets/newsfeed')
        assert newsfeed_res.status_code == 403
        assert json.loads(newsfeed_res.data)['code'] == code


class TestEndpoints:

    def test_get_user_fleets(self, client, app, name_to_id):
        url = '/api/users/{}/fleets'
        per_page = app.config['FLEETS_PER_PAGE']

        tanisha_url = url.format(name_to_id['Tanisha Jackson'])
        tanisha_res = client.get(tanisha_url)
        tanisha_data = json.loads(tanisha_res.data)
        assert tanisha_res.status_code == 200
        assert tanisha_data['success']
        assert tanisha_data['total_fleets'] == 9
        assert tanisha_data['total_following'] == 2
        assert tanisha_data['total_followers'] == 2
        assert len(tanisha_data['fleets']) <= per_page

        tracey_url = url.format(name_to_id['Tracey De Santa'])
        tracey_res = client.get(tracey_url)
        tracey_data = json.loads(tracey_res.data)
        assert tracey_res.status_code == 200
        assert tracey_data['success']
        assert tracey_data['total_fleets'] == 23
        assert tracey_data['total_following'] == 3
        assert tracey_data['total_followers'] == 3
        assert len(tracey_data['fleets']) <= per_page

        trevor_url = url.format(name_to_id['Trevor Philips'])
        trevor_res = client.get(trevor_url)
        trevor_data = json.loads(trevor_res.data)
        assert trevor_res.status_code == 200
        assert trevor_data['success']
        assert trevor_data['total_fleets'] == 0
        assert trevor_data['total_following'] == 0
        assert trevor_data['total_followers'] == 1
        assert len(trevor_data['fleets']) <= per_page

    def test_get_user_following(self, user_client, app, name_to_id):
        url = '/api/users/{}/following'
        per_page = app.config['USERS_PER_PAGE']

        lamar_url = url.format(name_to_id['Lamar Davis'])
        lamar_res = user_client.get(lamar_url)
        lamar_data = json.loads(lamar_res.data)
        assert lamar_res.status_code == 200
        assert lamar_data['success']
        assert lamar_data['total_fleets'] == 6
        assert lamar_data['total_following'] == 4
        assert lamar_data['total_followers'] == 9
        assert len(lamar_data['following']) <= per_page

        michael_url = url.format(name_to_id['Michael De Santa'])
        michael_res = user_client.get(michael_url)
        michael_data = json.loads(michael_res.data)
        assert michael_res.status_code == 200
        assert michael_data['success']
        assert michael_data['total_fleets'] == 0
        assert michael_data['total_following'] == 0
        assert michael_data['total_followers'] == 6
        assert len(michael_data['following']) <= per_page

    def test_get_user_followers(self, user_client, app, name_to_id):
        url = '/api/users/{}/followers'
        per_page = app.config['USERS_PER_PAGE']

        amanda_url = url.format(name_to_id['Amanda De Santa'])
        amanda_res = user_client.get(amanda_url)
        amanda_data = json.loads(amanda_res.data)
        assert amanda_res.status_code == 200
        assert amanda_data['success']
        assert amanda_data['total_fleets'] == 15
        assert amanda_data['total_following'] == 2
        assert amanda_data['total_followers'] == 5
        assert len(amanda_data['followers']) <= per_page

        floyd_url = url.format(name_to_id['Floyd Hebert'])
        floyd_res = user_client.get(floyd_url)
        floyd_data = json.loads(floyd_res.data)
        assert floyd_res.status_code == 200
        assert floyd_data['success']
        assert floyd_data['total_fleets'] == 0
        assert floyd_data['total_following'] == 1
        assert floyd_data['total_followers'] == 0
        assert len(floyd_data['followers']) <= per_page

    def test_get_newsfeed(self, user_client, app):
        res = user_client.get('/api/fleets/newsfeed')
        data = json.loads(res.data)

        assert res.status_code == 200
        assert data['success']
        assert data['total_fleets'] == 1
        assert data['total_following'] == 3
        assert data['total_followers'] == 0
        assert data['newsfeed_length'] == 21
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

    def test_422_get_user_items_invalid_args(self, user_client):
        fleets_res = user_client.get('/api/users/1/fleets?page=0')
        assert fleets_res.status_code == 422
        assert not json.loads(fleets_res.data)['success']

        following_res = user_client.get('/api/users/2/following?per_page=0')
        assert following_res.status_code == 422
        assert not json.loads(following_res.data)['success']

        followers_res = user_client.get('/api/users/3/followers?page=-1')
        assert followers_res.status_code == 422
        assert not json.loads(followers_res.data)['success']

        newsfeed_res = user_client.get('/api/fleets/newsfeed?per_page=-5')
        assert newsfeed_res.status_code == 422
        assert not json.loads(newsfeed_res.data)['success']

    def test_404_get_user_items_page_out_of_range(self, user_client,
                                                  name_to_id):
        trevor_url = f'/api/users/{name_to_id["Trevor Philips"]}'
        fleets_res = user_client.get(trevor_url + '/fleets?page=5')
        assert fleets_res.status_code == 404
        assert not json.loads(fleets_res.data)['success']

        michael_url = f'/api/users/{name_to_id["Michael De Santa"]}'
        following_res = user_client.get(michael_url + '/following?page=3')
        assert following_res.status_code == 404
        assert not json.loads(following_res.data)['success']

        floyd_url = f'/api/users/{name_to_id["Floyd Hebert"]}'
        followers_res = user_client.get(floyd_url + '/followers?page=3')
        assert followers_res.status_code == 404
        assert not json.loads(followers_res.data)['success']

        newsfeed_res = user_client.get('/api/fleets/newsfeed?page=5')
        assert newsfeed_res.status_code == 404
        assert not json.loads(newsfeed_res.data)['success']
