from flask_restful import Api, Resource, marshal_with, fields, reqparse
from flask import Blueprint, request
from utils.neo4j import graph
import model
from exts import session

bp = Blueprint("collection", __name__)
api = Api(bp)

# 解析参数
parser = reqparse.RequestParser()
parser.add_argument("page", type=int, location="args", help="当前页数")
parser.add_argument("per_page", type=int, location="args", help="每个多少个")

# 格式化返回值
response_fields = {
    'msg': fields.String(default="无效响应"),
    'code': fields.Integer(default=9999),
}
recipe_fields = {
    'id': fields.String(attribute='id'),
    'name': fields.String(attribute='name'),
    'picture': fields.String(attribute='picture'),
    'time_consuming': fields.String(attribute='time_consuming'),
    'process': fields.String(attribute='process'),
    'category': fields.List(fields.String, attribute="category"),
    'collect': fields.String(attribute="collect")
}
response_fields['data'] = fields.List(fields.Nested(recipe_fields), default=[])


class Collection(Resource):
    @marshal_with(response_fields)
    def get(self):  # todo 验证
        # 解析参数 获取某个用户收藏的所有食谱

        args = parser.parse_args()
        page = args.get("page")
        per_page = args.get("per_page")
        openid = request.environ['openid']
        user_id = request.environ['user_id']
        print("用户收藏的所有食谱", openid, page, per_page, user_id)
        try:
            # 获取第n页的m个食谱 其中n=page,m = per_page
            collections = model.CollectionModel.query.filter_by(user_id=user_id).offset((page - 1) * per_page).limit(
                per_page)

            # 收藏记录对应的食谱记录
            recipes = [collection.recipe for collection in collections]

            # collect属性
            for idx, item in enumerate(recipes):
                recipes[idx].collect = 1
                recipes[idx].category = recipes[idx].category.split('，')
            print(f"发现{len(recipes)}个食谱")
            return {"code": 10000, "msg": "查询成功", "data": recipes}
        except Exception as e:
            return {"code": 10001, "msg": e, "data": {}}
        # cypher = f"match (n:User) where n.openid = '{openid}' with n match (n)-[r:collect]->(m:Recipe) return m as recipe"
        # recipes = graph.run(cypher).data()
        # 格式化响应

    @marshal_with(response_fields)
    def post(self):
        # 解析参数
        parser = reqparse.RequestParser()
        parser.add_argument("openid", type=str, location="json")
        parser.add_argument("recipe_id", type=str, location="json")
        args = parser.parse_args()

        openid = request.environ['openid']  # 获取openid
        recipe_id = args.get("recipe_id")  # 获取recipe_id
        print(openid, recipe_id)
        user = model.UserModel.query.filter_by(openid=openid).first()
        collection = model.CollectionModel.query.filter_by(user_id=user.id, recipe_id=recipe_id).first()
        if not collection:  # 不存在收藏关系
            print("用户未收藏")
            # 添加收藏记录
            collection = model.CollectionModel(user_id=user.id, recipe_id=recipe_id)
            session.add(collection)

            # 所有食材
            cypher = f"match (n:Recipe)-[ne:need]->(i:Ingredient) where n.id = '{recipe_id}' return i as ingredient"
            ingredients = graph.run(cypher).data()
            # 交互记录
            for ingredient in ingredients:
                ingredient = ingredient['ingredient']
                interaction = model.User_IngredientModel.query.filter_by(user_id=user.id,ingredient_id=ingredient['id']).first()
                if interaction:  # 存在
                    interaction.collect_count = interaction.collect_count + 1
                else:  # 不存在
                    interaction = model.User_IngredientModel(user_id=user.id,ingredient_id=ingredient['id'],collect_count=1)
                    session.add(interaction)
            session.commit()
            return {"code": 10000, "msg": "收藏成功"}
        else:  # 存在收藏关系
            return {"code": 10002, "msg": "收藏失败！用户已收藏"}

    @marshal_with(response_fields)
    def delete(self):
        # 解析参数
        parser = reqparse.RequestParser()
        parser.add_argument("openid", type=str, location="json")
        parser.add_argument("recipe_id", type=str, location="json")
        args = parser.parse_args()

        # 获取参数
        openid = request.environ['openid']
        recipe_id = args.get("recipe_id")

        user = model.UserModel.query.filter_by(openid=openid).first()
        collection = model.CollectionModel.query.filter_by(user_id=user.id, recipe_id=recipe_id).first()
        if collection:  # 存在收藏关系
            print("用户已收藏")
            # 删除收藏记录
            session.delete(collection)

            # 所有食材
            cypher = f"match (n:Recipe)-[ne:need]->(i:Ingredient) where n.id = '{recipe_id}' return i as ingredient"
            ingredients = graph.run(cypher).data()
            # 交互记录
            for ingredient in ingredients:
                ingredient = ingredient['ingredient']
                interaction = model.User_IngredientModel.query.filter_by(user_id=user.id, ingredient_id=ingredient['id']).first()
                if interaction:  # 存在
                    print(f"{ingredient['id']}和{user.id}的交互记录存在")
                    interaction.collect_count = interaction.collect_count - 1
                else:  # 不存在
                    print(f"{ingredient['id']}和{user.id}的交互记录不存在")

                    interaction = model.User_IngredientModel(user_id=user.id, ingredient_id=ingredient['id'],
                                                             collect_count=0)
                    session.add(interaction)

            session.commit()
            return {"code": 10000, "msg": "取消收藏成功"}
        else:  # 不存在收藏关系
            return {"code": 10002, "msg": "取消失败！用户还未收藏"}


api.add_resource(Collection, '/collection')
