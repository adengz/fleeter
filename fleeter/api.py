from flask import Blueprint, request, current_app, abort, jsonify
from fleeter.models import User, Fleet


bp = Blueprint('api', __name__, url_prefix='/api')


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
def get_user_fleets(user_id: int):
    return _get_paginated_user_items(user_id=user_id, field='fleets')
