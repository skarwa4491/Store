from models import UserModel
from flask_smorest import abort,Blueprint
from resources.Schemas import UserSchema
from sqlalchemy.exc import SQLAlchemyError
from flask.views import MethodView
from passlib.hash import pbkdf2_sha256
from db import db
from flask_jwt_extended import create_access_token,jwt_required,get_jwt , create_refresh_token ,get_jwt_identity
from blocklist import blocklist

blp = Blueprint("Users", __name__ , description='Operation on users')

@blp.route("/register")
class UsersRegister(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(200 , UserSchema)
    def post(self,user_data):
        user = UserModel.query.filter(UserModel.user_id == user_data['user_id']).first()
        if user:
            abort(409 , 'user already present')
        user_id = user_data['user_id']
        password = pbkdf2_sha256.hash(user_data['password'])
        user = UserModel(user_id=user_id,password=password)
        db.session.add(user)
        db.session.commit()
        return user,201

@blp.route("/user/<string:id>")
class User(MethodView):
    @blp.response(200 , UserSchema)
    def get(self,id):
        user = UserModel.query.get_or_404(id)
        return user
    def delete(self,id):
        user = UserModel.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return {'message': 'user with user-id {user_id} is delete successfully'.format(user_id=id)},200
@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self,user_data):
        '''
            jwt_token is encoded string not hased , so it can be decoded
        '''
        user = UserModel.query.filter(user_data['user_id']==UserModel.user_id).first()
        if (user and pbkdf2_sha256.verify(user_data['password'],user.password)):
            access_token = create_access_token(identity=user.id , fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token" : access_token , 'refresh_token' : refresh_token}
        return {'message':'Invallid credentails'}

@blp.route('/logout')
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        blocklist.add(jti)
        return {'message' : 'logged out successfully'}
@blp.route('/refresh')
class UserRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_tokn = create_access_token(identity=current_user , fresh=False)
        return {"access_token" : new_tokn}

@blp.route("/user")
class UserList(MethodView):
    @blp.response(200 , UserSchema(many=True))
    def get(self):
        return UserModel.query.all()