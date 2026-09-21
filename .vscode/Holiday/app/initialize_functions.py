from flask import Flask
from flasgger import Swagger
from app.modules.main.route import main_bp
from app.modules.incidents.route import incidents_bp
from app.db.db import db


def initialize_route(app: Flask):
    with app.app_context():
        app.register_blueprint(main_bp, url_prefix='/api/v1/main')
        app.register_blueprint(incidents_bp, url_prefix='/api/v1/incidents')


def initialize_db(app: Flask):
    with app.app_context():
        db.init_app(app)
        db.create_all()

def initialize_swagger(app: Flask):
    with app.app_context():
        swagger = Swagger(app)
        return swagger