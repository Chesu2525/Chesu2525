{
  "title": "Flooded clinic",
  "description": "Water has entered the ground floor.",
  "category": "flood",
  "severity": "high",
  "latitude": 40.7128,
  "longitude": -74.006,
  "people_affected": 18
}from flask import Flask, jsonify
from app.config.config import get_config_by_name
from app.initialize_functions import initialize_route, initialize_db, initialize_swagger
from app.modules.main.controller import MainController


main_controller = MainController()

def create_app(config=None) -> Flask:
    """
    Create a Flask application.

    Args:
        config: The configuration object to use.

    Returns:
        A Flask application instance.
    """
    app = Flask(__name__)
    if config:
        app.config.from_object(get_config_by_name(config))

    # Initialize extensions
    initialize_db(app)

    # Register blueprints
    initialize_route(app)

    # Initialize Swagger
    initialize_swagger(app)

    @app.route("/", methods=["GET"])
    def index():
        return jsonify(main_controller.index())

    return app
