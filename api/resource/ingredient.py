from flask import Blueprint, request
from flask_restful import Resource,Api,reqparse,fields,marshal_with
from utils.neo4j import graph
from utils.recommend import recommend_recipes,ingredient_recommend_main

bp = Blueprint("ingredient",__name__)

api = Api(bp)

parser = reqparse.RequestParser()
parser.add_argument("recommend_ingredient_name",type= str,location="args",help="推荐食材的name")
parser.add_argument("recommend_target_num",type= int,location="args",help="推荐生成的食材个数")

response_fields = {
    'msg': fields.String(default="无效响应"),
    'code': fields.Integer(default=9999),
    'data':fields.List(fields.String())
}
class Ingredient(Resource):
    def get(self):
        # 解析参数
        args = parser.parse_args()
        recommend_ingredient_name = args.get("recommend_ingredient_name")
        recommend_target_num = args.get("recommend_target_num")

        # 调用util.recommend.ingredient_recommend_main
        try:
            ingredients_recommend = ingredient_recommend_main({"name":recommend_ingredient_name},recommend_target_num)
        except Exception as e:
            return {"code": 10001, "msg": "暂无推荐", "data": {}}

        ingredients_name_list_recommend = []  # 推荐食材name列表
        for item in ingredients_recommend:
            ingredients_name_list_recommend.append(item['name'])
        return {"code":10000,"msg":"查询成功","data":ingredients_name_list_recommend}

api.add_resource(Ingredient,'/ingredient')