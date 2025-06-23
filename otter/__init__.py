from flask import Flask

from otter.conf import settings
from otter.util_log import logger
from otter.util_resp import abort
from otter.view_message import route as route_message


def create_app():
    app = Flask('otter')  # noqa

    register_errors(app)
    register_blueprints(app)
    return app


def register_errors(app):  # noqa
    @app.errorhandler(404)
    def not_found(error):
        return abort(404)

    @app.errorhandler(405)
    def not_found(error):
        return abort(405)

    @app.errorhandler(Exception)
    def global_exception_handler(error):
        logger.exception(error)
        return abort(500)


def register_blueprints(app):  # noqa
    app.register_blueprint(route_message)


app = create_app()
