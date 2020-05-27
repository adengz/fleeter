from flask import Blueprint, request, current_app, abort, jsonify
from fleeter.models import User, Fleet


bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/<username>', methods=['GET'])
def get_user_fleets(username: str):
    username = username.replace('_', ' ')
    user = User.query.filter_by(username=username).first_or_404()
    response = user.to_dict()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page',
                                current_app.config['FLEETS_PER_PAGE'],
                                type=int)
    if page <= 0 or per_page <= 0:
        abort(422)
    paginated = user.fleet.paginate(page=page, per_page=per_page).items
    response['fleets'] = [f.to_dict() for f in paginated]
    response['success'] = True
    return jsonify(response)
