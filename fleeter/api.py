from __future__ import annotations

from flask import Blueprint, request, current_app, abort, jsonify
from fleeter.models import User, Fleet
from fleeter.auth import requires_auth


bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/', methods=['GET'])
def index():
    return jsonify({'success': True,
                    'message': 'Welcome! You just discovered fleeter.'})


def _get_user(auth0_id: str, raise_404: bool = True) -> User:
    user = User.query.filter_by(auth0_id=auth0_id).one_or_none()
    if user is None and raise_404:
        abort(404)
    return user


def _get_paginated_user_items(user_id: int, field: str):
    user = User.query.get_or_404(user_id)
    response = user.to_dict()

    page = request.args.get('page', 1, type=int)
    if field.startswith('follow'):
        default_per_page = current_app.config['USERS_PER_PAGE']
    else:
        default_per_page = current_app.config['FLEETS_PER_PAGE']
    per_page = request.args.get('per_page', default_per_page, type=int)
    if page <= 0 or per_page <= 0:
        abort(422)

    query = getattr(user, field)
    paginated = query.paginate(page=page, per_page=per_page).items
    response[field] = [i.to_dict() for i in paginated]
    if field == 'newsfeed':
        response['newsfeed_length'] = query.count()
    response['success'] = True
    return jsonify(response)


@bp.route('/users/<int:user_id>/fleets', methods=['GET'])
def get_user_fleets(user_id):
    return _get_paginated_user_items(user_id=user_id, field='fleets')


@bp.route('/users/<int:user_id>/following', methods=['GET'])
@requires_auth(permission='get:user_follow')
def get_user_following(payload, user_id):
    return _get_paginated_user_items(user_id=user_id, field='following')


@bp.route('/users/<int:user_id>/followers', methods=['GET'])
@requires_auth(permission='get:user_follow')
def get_user_followers(payload, user_id):
    return _get_paginated_user_items(user_id=user_id, field='followers')


@bp.route('/fleets/newsfeed', methods=['GET'])
@requires_auth(permission='get:newsfeed')
def get_newsfeed(payload):
    user_id = _get_user(payload['sub']).id
    return _get_paginated_user_items(user_id=user_id, field='newsfeed')


def _post_or_patch_fleet(auth0_id: str, patch: bool, fleet_id: int = None):
    user = _get_user(auth0_id)
    if patch:
        fleet = Fleet.query.get_or_404(fleet_id)
        if user != fleet.user:
            abort(403)
    else:
        fleet = Fleet(user=user)

    data = request.get_json()
    try:
        fleet.post = data['post']
        print('post' in data)
        assert fleet.post
    except KeyError:
        abort(400)
    except AssertionError:
        abort(422)

    try:
        fleet.update() if patch else fleet.insert()
    except:
        abort(500)
    return jsonify({'success': True, 'id': fleet.id})


@bp.route('/fleets', methods=['POST'])
@requires_auth(permission='post:fleets')
def post_fleet(payload):
    return _post_or_patch_fleet(payload['sub'], patch=False)


@bp.route('/fleets/<int:fleet_id>', methods=['PATCH'])
@requires_auth(permission='patch:fleets')
def patch_fleet(payload, fleet_id):
    return _post_or_patch_fleet(payload['sub'], patch=True, fleet_id=fleet_id)


@bp.route('/fleets/<int:fleet_id>', methods=['DELETE'])
@requires_auth(permission='delete:fleets')
def delete_fleet(payload, fleet_id):
    user = _get_user(payload['sub'], raise_404=False)
    fleet = Fleet.query.get_or_404(fleet_id)
    if user is not None and user != fleet.user:  # Neither moderator nor owner
        abort(403)

    try:
        fleet.delete()
    except:
        abort(500)
    return jsonify({'success': True, 'id': fleet_id})


@bp.route('/follows/<int:user_id>', methods=['POST', 'DELETE'])
@requires_auth(permission='follow/unfollow')
def follow_or_unfollow(payload, user_id):
    user = _get_user(payload['sub'])
    other = User.query.get_or_404(user_id)

    try:
        action = 'follow' if request.method == 'POST' else 'unfollow'
        getattr(user, action)(other)
        user.update()
    except AssertionError:
        abort(422)
    except:
        abort(500)
    return jsonify({'success': True, 'id': user_id})


@bp.route('/users/<int:user_id>', methods=['DELETE'])
@requires_auth(permission='delete:users')
def delete_user(payload, user_id):
    user = User.query.get_or_404(user_id)

    try:
        user.delete()
    except:
        abort(500)
    return jsonify({'success': True, 'id': user_id})
