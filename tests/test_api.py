import json


def test_get_user_fleets(client, app, name_to_id):
    per_page = app.config['FLEETS_PER_PAGE']
    url = '/api/users/{}/fleets'

    tanisha_res = client.get(url.format(name_to_id['Tanisha Jackson']))
    tanisha_data = json.loads(tanisha_res.data)
    assert tanisha_res.status_code == 200
    assert tanisha_data['success']
    assert tanisha_data['total_fleets'] == 9
    assert tanisha_data['total_following'] == 2
    assert tanisha_data['total_followers'] == 2
    assert len(tanisha_data['fleets']) <= per_page

    tracey_res = client.get(url.format(name_to_id['Tracey De Santa']))
    tracey_data = json.loads(tracey_res.data)
    assert tracey_res.status_code == 200
    assert tracey_data['success']
    assert tracey_data['total_fleets'] == 23
    assert tracey_data['total_following'] == 3
    assert tracey_data['total_followers'] == 3
    assert len(tracey_data['fleets']) <= per_page

    trevor_res = client.get(url.format(name_to_id['Trevor Philips']))
    trevor_data = json.loads(trevor_res.data)
    assert trevor_res.status_code == 200
    assert trevor_data['success']
    assert trevor_data['total_fleets'] == 0
    assert trevor_data['total_following'] == 0
    assert trevor_data['total_followers'] == 1
    assert len(trevor_data['fleets']) <= per_page

    print(name_to_id)


def test_404_get_user_fleets_page_out_of_range(client, name_to_id):
    url = '/api/users/{}/fleets'.format(name_to_id['Trevor Philips'])
    res = client.get(url + '?page=2')
    assert res.status_code == 404
    assert not json.loads(res.data)['success']


# def test_get_user_following(client, app):
#     per_page = app.config['USERS_PER_PAGE']
#
#     lamar_res = client.get('/api/Lamar_Davis/following')
#     lamar_data = json.loads(lamar_res.data)
#     assert lamar_res.status_code == 200
#     assert lamar_data['success']
#     assert lamar_data['total_fleets'] == 6
#     assert lamar_data['total_following'] == 4
#     assert lamar_data['total_followers'] == 9
#     assert len(lamar_data['following']) <= per_page
#
#     michael_res = client.get('/api/Michael_De_Santa/following')
#     michael_data = json.loads(michael_res.data)
#     assert michael_res.status_code == 200
#     assert michael_data['success']
#     assert michael_data['total_fleets'] == 0
#     assert michael_data['total_following'] == 0
#     assert michael_data['total_followers'] == 6
#     assert len(michael_data['following']) <= per_page
#
#
# def test_404_get_user_following_page_out_of_range(client):
#     res = client.get('/api/Michael_De_Santa/following?page=2')
#     assert res.status_code == 404
#     assert not json.loads(res.data)['success']
#
#
# def test_get_user_followers(client, app):
#     per_page = app.config['USERS_PER_PAGE']
#
#     amanda_res = client.get('/api/Amanda_De_Santa/followers')
#     amanda_data = json.loads(amanda_res.data)
#     assert amanda_res.status_code == 200
#     assert amanda_data['success']
#     assert amanda_data['total_fleets'] == 15
#     assert amanda_data['total_following'] == 2
#     assert amanda_data['total_followers'] == 5
#     assert len(amanda_data['followers']) <= per_page
#
#     floyd_res = client.get('/api/Floyd_Hebert/followers')
#     floyd_data = json.loads(floyd_res.data)
#     assert floyd_res.status_code == 200
#     assert floyd_data['success']
#     assert floyd_data['total_fleets'] == 0
#     assert floyd_data['total_following'] == 1
#     assert floyd_data['total_followers'] == 0
#     assert len(floyd_data['followers']) <= per_page
#
#
# def test_404_get_user_followers_page_out_of_range(client):
#     res = client.get('/api/Floyd_Hebert/followers?page=2')
#     assert res.status_code == 404
#     assert not json.loads(res.data)['success']
#
#
# def test_404_get_user_items_user_not_found(client):
#     non_exist_user = 'Michael_Townley'
#
#     fleets_res = client.get(f'/api/{non_exist_user}')
#     assert fleets_res.status_code == 404
#     assert not json.loads(fleets_res.data)['success']
#
#     following_res = client.get(f'/api/{non_exist_user}/following')
#     assert following_res.status_code == 404
#     assert not json.loads(following_res.data)['success']
#
#     followers_res = client.get(f'/api/{non_exist_user}/followers')
#     assert followers_res.status_code == 404
#     assert not json.loads(followers_res.data)['success']
#
#
# def test_422_get_user_items_invalid_args(client):
#     res1 = client.get('/api/Trevor_Philips?page=0')
#     assert res1.status_code == 422
#     assert not json.loads(res1.data)['success']
#
#     res2 = client.get('/api/Michael_De_Santa/following?per_page=0')
#     assert res2.status_code == 422
#     assert not json.loads(res2.data)['success']
