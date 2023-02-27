from flask_smorest import Blueprint , abort
from flask.views import MethodView
from resources.Schemas import TagSchema,PlainTagSchmea , TagAndItemSchema
from db import db
from models import ItemModel , StoreModel , TagModel
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("tags" , __name__ , description = 'operation on tags')

@blp.route("/store/<string:store_id>/tag")
class Tags(MethodView):

    # this will return all tags , at given store
    @blp.response(200 ,PlainTagSchmea(many=True))
    def get(self,store_id):
        store  = StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self,tag_data,store_id):
        if(TagModel.query.filter(TagModel.store_id == store_id , TagModel.tag_name == tag_data['tag_name']).first()):
            abort(400 , message = "Tag is already created")
        tag = TagModel(store_id = store_id , **tag_data)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500 , message= str(e))
        return tag

@blp.route("/tag/<string:tag_id>")
class TagsList(MethodView):

    @blp.response(200 , PlainTagSchmea)
    def get(self,tag_id):
        return TagModel.query.get_or_404(tag_id)

    def delete(self,tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        if(tag):
            db.session.delete(tag)
            db.session.commit()
        return {"message" : "tag deleted successfully"}

@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView):

    @blp.response(201, TagSchema)
    def post(self, item_id , tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500 , message=str(e))
        return tag

    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return {"message" : "item removed from tag ", "item" : item.item_name , "tag" : tag.tag_name    }

