from flask_smorest import Blueprint , abort
from flask.views import MethodView
from resources.Schemas import ItemSchema,ItemUpdateSchema
from db import db
from models import ItemModel
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required , get_jwt
blp = Blueprint("items" , __name__ , description="operation on items")

@blp.route("/item/<string:item_id>")
class Items(MethodView):

    @blp.response(200 , ItemSchema)
    def get(self,item_id):
        return ItemModel.query.get_or_404(item_id)

    @jwt_required()
    def delete(self,item_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="admin privilege required")
        item = ItemModel.query.get(item_id)
        if not item :
            return {'message': 'Item you are trying to delete is not present'}
        db.session.delete(item)
        db.session.commit()
        return {"message" : "item deleted successfully"}


    @blp.arguments(ItemUpdateSchema)
    @blp.response(200 ,ItemSchema)
    def put(self,item_data,item_id):
        item = ItemModel.query.get(item_id)
        if item:
            item.item_name = item_data["item_name"]
            item.item_price = item_data['item_price']
        else:
            item = ItemModel(item_id = item_id , **item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500 , message=str(e))

        return item

@blp.route("/item")
class ItemList(MethodView):

    @blp.response(200,ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @jwt_required() # pass header authorization : Bearer <access token>
    @blp.arguments(ItemSchema)
    @blp.response(200 , ItemSchema)
    def post(self,item_data):
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return item
