import json


def test_get_user_fleets(client):
    denise_res = client.get('/api/Denise_Clinton')
    denise_data = json.loads(denise_res.data)
    assert denise_res.status_code == 200
    assert denise_data['success']
    assert denise_data['total_fleets'] == 10
    assert denise_data['following'] == 1
    assert denise_data['followers'] == 3

    tracey_res = client.get('/api/Tracey_De_Santa')
    tracey_data = json.loads(tracey_res.data)
    assert tracey_res.status_code == 200
    assert tracey_data['success']
    assert tracey_data['total_fleets'] == 23
    assert tracey_data['following'] == 3
    assert tracey_data['followers'] == 3


def test_404_get_user_fleets_user_not_found(client):
    res = client.get('/api/Michael_Townley')
    assert res.status_code == 404
    assert not json.loads(res.data)['success']


def test_422_get_user_fleets_invalid_args(client):
    res1 = client.get('/api/Trevor_Philips?page=0')
    assert res1.status_code == 422
    assert not json.loads(res1.data)['success']

    res2 = client.get('/api/Trevor_Philips?per_page=0')
    assert res2.status_code == 422
    assert not json.loads(res2.data)['success']


def test_404_get_user_fleets_page_out_of_range(client):
    res = client.get('/api/Trevor_Philips?page=2')
    assert res.status_code == 404
    assert not json.loads(res.data)['success']
