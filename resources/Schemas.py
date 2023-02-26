from marshmallow import fields , Schema

class PlainStoreSchema(Schema):
    store_id = fields.Integer(dump_only=True)
    store_name = fields.String(required=True)

class PlainItemSchema(Schema):
    item_id = fields.Integer(dump_only=True)
    item_name = fields.String(required=True)
    item_price = fields.Integer(required=True)

class PlainTagSchmea(Schema):
    tag_id = fields.Integer(dump_only=True)
    tag_name = fields.String(required=True)

class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchmea()) , dump_only=True)

class ItemSchema(PlainItemSchema):
    store_id = fields.Integer(required=True)
    #items = fields.Nested(PlainStoreSchema() , dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchmea), dump_only=True)

class TagSchema(PlainTagSchmea):
    #store_id = fields.Integer(dump_only=True)
    store = fields.Nested(PlainStoreSchema())
    items = fields.List(fields.Nested(PlainItemSchema(), dump_only=True))

class ItemUpdateSchema(Schema):
    item_price = fields.Integer(required=True)
    item_name = fields.String(required=True)

class TagAndItemSchema(Schema):
    message = fields.String()
    item = fields.Nested(ItemSchema())
    tag = fields.Nested(TagSchema())