# fleeter
A minimal (minimal API only) twitter clone built on Flask.

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

Working within a virtual environment is recommended whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by running:

```bash
% pip install -r requirements.txt
```

This will install all of the required packages within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) are libraries to work with the PostgreSQL database. 

- [jose](https://python-jose.readthedocs.io/en/latest/) JavaScript Object Signing and Encryption for JWTs. Useful for encoding, decoding, and verifying JWTS.

- [pytest](https://docs.pytest.org/en/latest/) is a third-party testing framework with a more pythonic syntax for writing tests.

## Running the server

With a PostgreSQL server running locally, create a new db `fleeter` by running 

```
% dropdb fleeter
% createdb fleeter
```

From within the root directory first ensure you are working using your created virtual environment.

To run the server, execute:

```
% source setup.sh
% flask db upgrade  # must not skip for the first time
% flask run
```

## Testing

With a PostgreSQL server running locally, create a new testing db `fleeter_test` by running

```
% dropdb fleeter_test
% createdb fleeter_test
```

From within the root directory first ensure you are working using your created virtual environment.

To run all the tests, execute:

```
% source setup.sh
% pytest
```

Or to run tests for models and api separately, execute:

```
% source setup.sh
% pytest tests/test_models.py
% pytest tests/test_api.py
```

## Deployment on Heroku

The API is now live on <https://fleeeterrr.herokuapp.com>, with the database hosting the same mock data for integration tests. Try hit a public endpoint <https://fleeeterrr.herokuapp.com/api/users/1/fleets>.

_For project reviewer_

_To test other endpoints requiring authorization, login with the provided credential from the home page (using incognito mode since no logout option is available). Copy the JWT from the response URL. This is dumb as hell and why we need a frontend._

## API Documentation

### Endpoints

```
GET "/api/users/<int:user_id>/fleets"
GET "/api/users/<int:user_id>/following"
GET "/api/users/<int:user_id>/followers"
GET "/api/fleets/newsfeed"
POST "/api/fleets"
PATCH "/api/fleets/<int:fleet_id>"
DELETE "/api/fleets/<int:fleet_id>"
POST "/api/follows/<int:user_id>"
DELETE "/api/follows/<int:user_id>"
DELETE "/api/users/<int:user_id>"
```

### Roles and Role-Based-Access-Control (RBAC)

Two roles require authorization:

- **User**: Regular user, with permissions to interact with other users (follow/unfollow), create a fleet, edit/delete a fleet as owner, and fetch newsfeed. 
- **Moderator**: Moderator, with special permissions to delete any fleet or user, but no regular user permissions.

#### Endpoint Accessibility by Role

| Endpoint | Unauthroized | User | Moderator |
| --- | --- | --- | --- |
|`GET "/api/users/<int:user_id>/fleets"`|True|True|True|
|`GET "/api/users/<int:user_id>/following"`|False|True|True|
|`GET "/api/users/<int:user_id>/followers""`|False|True|True|
|`GET "/api/fleets/newsfeed"`|False|True|False|
|`POST "/api/fleets"`|False|True|False|
|`PATCH "/api/fleets/<int:fleet_id>"`|False|True (owner)|False|
|`DELETE "/api/fleets/<int:fleet_id>"`|False|True (owner)|True|
|`POST "/api/follows/<int:user_id>"`|False|True|False|
|`DELETE "/api/follows/<int:user_id>"`|False|True|False|
|`DELETE "/api/users/<int:user_id>"`|False|False|True|

### Behavior of Each Endpoint

#### `GET "/api/users/<int:user_id>/fleets"`
- Fetches paginated fleets posted by user with `user_id`, sorted by reverse chronological order. 
- Authorized roles: Public.
- Request arguments: 
	- `int page`: Page number, default to 1
	- `int per_page`: Number of fleets per page, default to 10
- Request body: None.
- Raises: 
	- 404: User with `user_id` does not exist.
	- 422: Non positive `page` or `per_page`.
	- 404: No items found for a large (> 1) `page`.
- Returns: User information (`id`, `username`, `total_fleets`, `total_following`, `total_followers`) and paginated `fleets`.
- Response body: 

```
"id": 4,
"username": "Trevor", 
"total_fleets": 5, 
"total_following": 1,
"total_followers": 1,
"fleets": [
	{
		"id": 16, 
		"post": "Friends Reunited", 
		"username": "Trevor", 
		"created_at": "2020-05-31 14:47:32.549421"
	},
	...
	{
		"id": 12, 
		"post": "Mr. Philips", 
		"username": "Trevor", 
		"created_at": "2020-05-31 14:46:08.549421"
	}
]
```

#### `GET "/api/users/<int:user_id>/following"`
- Fetches paginated users being followed by user with `user_id`, sorted by reverse chronological order. 
- Authorized roles: User and Moderator.
- Request arguments: 
	- `int page`: Page number, default to 1
	- `int per_page`: Number of fleets per page, default to 10
- Request body: None.
- Raises: 
	- 404: User with `user_id` does not exist.
	- 422: Non positive `page` or `per_page`.
	- 404: No items found for a large (> 1) `page`.
- Returns: User information (`id`, `username`, `total_fleets`, `total_following`, `total_followers`) and paginated `following`.
- Response body: 

```
"id": 3,
"username": "Franklin", 
"total_fleets": 4, 
"total_following": 1,
"total_followers": 1,
"following": [
	{
		"id": 2, 
		"username": "Michael", 
		"total_fleets": 7,
		"total_following": 1, 
		"total_followers": 3,
	}
]
```

#### `GET "/api/users/<int:user_id>/followers"`
- Fetches paginated users now following the user with `user_id`, sorted by reverse chronological order. 
- Authorized roles: User and Moderator.
- Request arguments: 
	- `int page`: Page number, default to 1
	- `int per_page`: Number of fleets per page, default to 10
- Request body: None.
- Raises: 
	- 404: User with `user_id` does not exist.
	- 422: Non positive `page` or `per_page`.
	- 404: No items found for a large (> 1) `page`.
- Returns: User information (`id`, `username`, `total_fleets`, `total_following`, `total_followers`) and paginated `followers`.
- Response body: 

```
"id": 2,
"username": "Michael", 
"total_fleets": 7, 
"total_following": 1,
"total_followers": 3,
"followers": [
	{
		"id": 1, 
		"username": "player", 
		"total_fleets": 1,
		"total_following": 2, 
		"total_followers": 0,
	},
	{
		"id": 4, 
		"username": "Trevor", 
		"total_fleets": 5,
		"total_following": 1, 
		"total_followers": 1,
	}
]
```


#### `GET "/api/fleets/newsfeed"`
- Fetches paginated newsfeed of current user, including fleets posted from the user and all users currently being followed, sorted by reverse chronological order. 
- Authorized roles: User only.
- Request arguments: 
	- `int page`: Page number, default to 1
	- `int per_page`: Number of fleets per page, default to 10
- Request body: None.
- Raises: 
	- 422: Non positive `page` or `per_page`.
	- 404: No items found for a large (> 1) `page`.
- Returns: User information (`id`, `username`, `total_fleets`, `total_following`, `total_followers`) and paginated `newsfeed`.
- Response body: 

```
"id": 1,
"username": "player", 
"total_fleets": 1, 
"total_following": 2,
"total_followers": 0,
"newsfeed_length": 13,
"newsfeed": [
	{
		"id": 17, 
		"post": "Hola, Los Santos", 
		"username": "player", 
		"created_at": "2020-05-31 14:47:38.549421"
	},
	...
	{
		"id": 8, 
		"post": "Daddy's Little Girl", 
		"username": "Michael", 
		"created_at": "2020-05-31 14:46:44.549421"
	}
]
```

#### `POST "/api/fleets"`
- Creates a fleet.
- Authorized roles: User only.
- Request arguments: None.
- Request body: `"post": "Fame or Shame"`.
- Raises: 
	- 400: Key `"post"` not in request body.
	- 422: Value of key `"post"` is empty (`""`) or None.
- Returns: `id` of newly created fleet. 
- Response body: `"id": fleet_id`

#### `PATCH "/api/fleets/<int:fleet_id>"`
- Edits a fleet post with given id.
- Authorized roles: User (owner) only.
- Request arguments: None.
- Request body: `"post": "Fame or Shame"`.
- Raises: 
	- 404: Fleet with `fleet_id` does not exist.
	- 400: Key `"post"` not in request body.
	- 422: Value of key `"post"` is empty (`""`) or None.
- Returns: None. 
- Response body: `"id": fleet_id`

#### `DELETE "/api/fleets/<int:fleet_id>"`
- Deletes a fleet with given id.
- Authorized roles: User (owner) and Moderator.
- Request arguments: None.
- Request body: None.
- Raises: 
	- 404: Fleet with `fleet_id` does not exist.
- Returns: None. 
- Response body: `"id": fleet_id`

#### `POST "/api/follows/<int:user_id>"`
- Follows a user with given id.
- Authorized roles: User only.
- Request arguments: None.
- Request body: None.
- Raises: 
	- 404: User with `user_id` does not exist.
	- 422: Current user's id is the same as `user_id`, i.e., attempt to follow self. 
- Returns: None. 
- Response body: `"id": user_id`

#### `DELETE "/api/follows/<int:user_id>"`
- Unfollows a user with given id.
- Authorized roles: User only.
- Request arguments: None.
- Request body: None.
- Raises: 
	- 404: User with `user_id` does not exist.
	- 422: Current user's id is the same as `user_id`, i.e., attempt to unfollow self. 
- Returns: None. 
- Response body: `"id": user_id`

#### `DELETE "/api/users/<int:user_id>"`
- Deletes a user with given id.
- Authorized roles: Moderator only.
- Request arguments: None.
- Request body: None.
- Raises: 
	- 404: User with `user_id` does not exist.
- Returns: None. 
- Response body: `"id": user_id`
