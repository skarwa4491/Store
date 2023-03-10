from flask_smorest import Blueprint , abort
from flask.views import MethodView
from db import db
from resources.Schemas import StoreSchema
from models import StoreModel , ItemModel
from sqlalchemy.exc import SQLAlchemyError
blp = Blueprint("store" , __name__ , description="operation on stores")

@blp.route("/store/<string:id>")
class Store(MethodView):

    @blp.response(200 , StoreSchema)
    def get(self,id):
        return StoreModel.query.get_or_404(id)

    def delete(self,id):
        store  = StoreModel.query.get_or_404(id)
        db.session.delete(store)
        db.session.commit()
        return {"message" : "Store Deleted"}

@blp.route("/store")
class StoreList(MethodView):

    @blp.response(200 , StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(200 , StoreSchema)
    def post(self,store_data):
        item_list = None
        if 'items' in store_data:
            item_list = store_data.pop('items')
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500 , message=str(e))
        if item_list:
            for item in item_list:
                item_object = ItemModel(store_id = store.store_id , **item)
                db.session.add(item_object)
                db.session.commit()
        return store

