import os

from flask import Flask
from db import db
from flask_smorest import Api
import models
from resources.Stores import blp as StoreBluePrint
from resources.Items import blp as ItemBluePrint
from resources.Tags import blp as TagBluePrint
from resources.Users import blp as UserBluePrint
from flask_jwt_extended.jwt_manager import JWTManager
import secrets
from flask import jsonify
from blocklist import blocklist


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
    #secrets.SystemRandom().getrandbits(128)
    app.config['JWT_SECRET_KEY'] = "252607315970867712777744764892655702725"
    jwt = JWTManager(app)
    @jwt.token_in_blocklist_loader
    def check_if_token_in_block_list(jwt_header , jwt_payload):
        '''
            this is used to check if access token is in block list
        '''
        return jwt_payload['jti'] in blocklist

    @jwt.revoked_token_loader
    def revoked_token(jwt_header , jwt_payload):
        '''
            this is used , when we are trying to use an access token which is blocked
        '''
        return (jsonify({
            'message': 'you are logged out, login again',
            'error': 'token blacklisted',
            'jwt_header': jwt_header,
            'jwt_payload': jwt_payload
        }), 401)

    @jwt.additional_claims_loader
    def claim(identity):
        if identity == 2:
            return {'is_admin': True}
        else:
            return {'is_admin' : False}
    @jwt.expired_token_loader
    def expeired_token(jwt_header , jwt_payload):
        '''
            this is used , when we are using and expeired token
        '''
        return (jsonify({
            'message': 'token has expeired',
            'error' :'token expeired',
            'jwt_header' : jwt_header,
            'jwt_payload' : jwt_payload
        }),401)
    @jwt.invalid_token_loader
    def invalid_token(error):
        '''
            this is used when we are using an invalid token
        '''
        return jsonify({
        'message':'try creating a new token',
        'error' : 'invlid token'
    },401)

    @jwt.unauthorized_loader
    def unauthorized(error):
        '''

            this is used when authorization is not passed in headers
        '''
        return jsonify(
            {'message': 'you are not authorized' ,
             'error' : 'authorization required' + error}
        ) , 401

    api.register_blueprint(StoreBluePrint)
    api.register_blueprint(ItemBluePrint)
    api.register_blueprint(TagBluePrint)
    api.register_blueprint(UserBluePrint)
    return app