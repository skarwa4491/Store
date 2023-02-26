import os

from flask import Flask
from db import db
from flask_smorest import Api
import models
from resources.Stores import blp as StoreBluePrint
from resources.Items import blp as ItemBluePrint
from resources.Tags import blp as TagBluePrint
from flask_jwt_extended.jwt_manager import JWTManager
import secrets


def create_app(db_url=None):
    app = Flask(__name__)
    app.config["PROPOGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Store REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL","sqlite:///data.db")
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    db.init_app(app)
    with app.app_context(): # this is updated , instead of @app.before_first_request
        db.create_all()
    api = Api(app)
    app.config['JWT_SECRET_KEY'] = secrets.SystemRandom().getrandbits(128)
    jwt = JWTManager(app)
    api.register_blueprint(StoreBluePrint)
    api.register_blueprint(ItemBluePrint)
    api.register_blueprint(TagBluePrint)
    return app