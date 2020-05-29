from __future__ import annotations

from flask import Blueprint, request, current_app, abort, jsonify
from fleeter.models import User, Fleet
from fleeter.auth import requires_auth


bp = Blueprint('api', __name__, url_prefix='/api')


def _get_user(auth0_id: str) -> User:
    return User.query.filter_by(auth0_id=auth0_id).one_or_none()


def _owns(user: User, fleet: Fleet) -> bool:
    return user == fleet.user


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


@bp.route('/fleets', methods=['POST'])
@requires_auth(permission='post:fleets')
def post_fleet(payload):
    return 'Not implemented'


@bp.route('/fleets/<int:fleet_id>', methods=['PATCH'])
@requires_auth(permission='patch:fleets')
def patch_fleet(payload, fleet_id):
    return 'Not implemented'


@bp.route('/fleets/<int:fleet_id>', methods=['DELETE'])
@requires_auth(permission='delete:fleets')
def delete_fleet(payload, fleet_id):
    return 'Not implemented'


@bp.route('/follows/<int:user_id>', methods=['POST', 'DELETE'])
@requires_auth(permission='follow/unfollow')
def follow_or_unfollow(payload, user_id):
    return 'Not implemented'


@bp.route('/users/<int:user_id>', methods=['DELETE'])
@requires_auth(permission='delete:users')
def delete_user(payload, user_id):
    return 'Not implemented'
