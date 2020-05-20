from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()


def create_app(config='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,POST,PATCH,DELETE,OPTIONS')
        return response

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'success': False,
                        'error': 400,
                        'message': 'Bad request'}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False,
                        'error': 404,
                        'message': 'Not found'}), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({'success': False,
                        'error': 422,
                        'message': 'Unprocessable'}), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({'success': False,
                        'error': 500,
                        'message': 'Internal server error'}), 500

    return app
