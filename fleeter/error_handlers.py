from flask import Blueprint, jsonify
from fleeter import db
from fleeter.auth import AuthError


bp = Blueprint('errors', __name__)


@bp.app_errorhandler(400)
def bad_request(error):
    return jsonify({'success': False, 'error': 400,
                    'message': 'Bad request'}), 400


@bp.app_errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 404,
                    'message': 'Not found'}), 404


@bp.app_errorhandler(422)
def unprocessable(error):
    return jsonify({'success': False, 'error': 422,
                    'message': 'Unprocessable'}), 422


@bp.app_errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return jsonify({'success': False, 'error': 500,
                    'message': 'Internal server error'}), 500


@bp.app_errorhandler(AuthError)
def auth_error(ex):
    response = {'success': False}
    response.update(ex.error)
    return jsonify(response), ex.status_code
