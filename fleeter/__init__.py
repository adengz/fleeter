import os
from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()


def create_app(config='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,POST,PATCH,DELETE,OPTIONS')
        return response

    from fleeter.error_handlers import bp as errors_bp
    app.register_blueprint(errors_bp)

    from fleeter.api import bp as api_bp
    app.register_blueprint(api_bp)

    from fleeter.auth import AUTH0_DOMAIN, API_AUDIENCE
    CLIENT_ID = os.environ['CLIENT_ID']

    @app.route('/')
    @app.route('/login')
    def login():
        return redirect(f'https://{AUTH0_DOMAIN}/authorize?'
                        f'audience={API_AUDIENCE}&'
                        f'response_type=token&'
                        f'client_id={CLIENT_ID}&'
                        f'redirect_uri=https://fleeeterrr.herokuapp.com/api')

    return app
