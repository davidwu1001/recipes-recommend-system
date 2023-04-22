from flask import Blueprint, request
from flask_restful import Resource,Api,reqparse,fields,marshal_with
from utils.neo4j import graph
from utils.recommend import recommend_recipes,ingredient_recommend_recipe
bp = Blueprint("recipe",__name__)
api = Api(bp)

parser = reqparse.RequestParser()
parser.add_argument("recipe_id",type=str,location="args",help="id不能为空")
parser.add_argument("name",type=str,location="args",help="姓名的格式错误")
parser.add_argument("season",type=str,location="args",help="季节的格式错误")
parser.add_argument("category",type=str,location="args",help="菜品的格式错误")
parser.add_argument("openid",type= str,location="args",help="用户openid的格式错误")
parser.add_argument("hot",type= str,location="args",help="用户openid的格式错误")
parser.add_argument("recommend_recipe_id",type= str,location="args",help="推荐食谱的id")
parser.add_argument("recommend_target_num",type= int,location="args",help="推荐生成的食谱个数")
parser.add_argument("recommend_ingredient_name",type= str,location="args",help="推荐食材的name")


response_fields = {
    'msg': fields.String(default="无效响应"),
    'code': fields.Integer(default=9999),
}
procedures_fields = {
    "id":fields.String(),
    "picture": fields.String(),
    "seq":fields.String(),
    "text":fields.String()
}
ingredient_fields = {
    "id":fields.String(),
    "name":fields.String(),
    "amount":fields.String(),
}
recipe_fields = {
    'id':fields.String(attribute='recipe.id'),
    'name':fields.String(attribute='recipe.name'),
    'picture':fields.String(attribute='recipe.picture'),
    'text':fields.String(attribute='recipe.text'),
    'time_consuming':fields.String(attribute='recipe.time_consuming'),
    'process':fields.String(attribute='recipe.process'),
    'category':fields.List(fields.String,attribute="recipe.category"),
    'collect':fields.Integer(),
    'ingredients':fields.List(fields.Nested(ingredient_fields)),
    'procedures': fields.List(fields.Nested(procedures_fields))
}

response_fields['data'] = fields.List(fields.Nested(recipe_fields))


class Recipe(Resource):
    @marshal_with(response_fields)
    def get(self):
        #查询食谱
        args = parser.parse_args()
        recipe_id = args.get('recipe_id')
        name = args.get("name")
        season = args.get("season")
        category = args.get("category")
        openid = request.environ['openid']
        recommend_recipe_id = args.get("recommend_recipe_id")
        recommend_target_num = args.get("recommend_target_num")
        recommend_ingredient_name = args.get("recommend_ingredient_name")
        hot = args.get("hot")
        print(recipe_id, openid)
        if recipe_id:
            #根据id查询菜谱
            print("根据id查询菜谱",recipe_id)
            cypher = f"MATCH (r:Recipe) WHERE r.id = '{recipe_id}' OPTIONAL MATCH (u:User)-[c:collect]->(r) WHERE u.openid = '{openid}' OPTIONAL MATCH (r)-[n:need]->(i:Ingredient) OPTIONAL MATCH (r)-[s:step]->(p:Procedure) WITH r AS recipe, coalesce(count(c)) AS collect, collect(i) AS ingredients, collect(n.amount) AS amounts, p ORDER BY p.seq WITH recipe, collect, ingredients, amounts, collect(p) AS procedures UNWIND range(0,size(ingredients)-1) as idx WITH recipe, collect, apoc.map.setKey(ingredients[idx], 'amount', amounts[idx]) AS ingredient, procedures RETURN recipe, collect, collect(ingredient) AS ingredients, procedures"
            res = graph.run(cypher).data()
            return {"code":10000,"msg":"查询成功","data":res}
        elif recommend_recipe_id and recommend_target_num:  # 查询推荐食谱
            print("由食谱推荐食谱")
            recipes_recommend = recommend_recipes({"id":recommend_recipe_id},recommend_target_num)  # 调用util.recommend.recommend_recipes

            recipes_id_list = []  # 生成的推荐食谱id列表
            for recipe in recipes_recommend:
                recipes_id_list.append(recipe['id'])

            cypher = f'match (r:Recipe) where r.id in {str(recipes_id_list)} return r as recipe'
            res = graph.run(cypher).data()
            return {"code": 10000, "msg": "推荐生成完成", "data": res}
        elif recommend_ingredient_name and recommend_target_num:
            print("由食材推荐食谱")
            recipes_recommend = ingredient_recommend_recipe({'name':recommend_ingredient_name},recommend_target_num)  # 调用util.recommend.ingredient_recommend_recipe

            recipes_id_list = []  # 生成的推荐食谱id列表
            for recipe in recipes_recommend:
                recipes_id_list.append(recipe['id'])

            cypher = f"match (r:Recipe)-[n:need]->(i:Ingredient) where r.id in {str(recipes_id_list)} and i.name = '{recommend_ingredient_name}'  return r as recipe"
            print(cypher)
            res = graph.run(cypher).data()
            return {"code": 10000, "msg": "推荐生成完成", "data": res}

        elif category:
            #根据菜品查询食谱
            print("根据菜品查询食谱")
            if category == "不限":
                cypher = f"match (n:Recipe) where n.name contains '{name}' optional match (u:User)-[col:collect]->(n) where u.openid = '{openid}' return n as recipe, coalesce(count(col)) as collect limit 10"
            else:
                cypher = f"match (n:Recipe) where n.name contains '{name}' and '{category}' in n.category optional match (u:User)-[col:collect]->(n) where u.openid = '{openid}' return n as recipe, coalesce(count(col)) as collect limit 10"
            res = graph.run(cypher).data()
            print(res)
            return {"code":10000,"msg":"查询成功","data":res}
        elif hot:
            # 根据流行程度查询六个菜谱 todo:如何体现热门 当前是默认排序
            print("根据流行程度查询六个菜谱")
            cypher = "match (n:Recipe) return n as recipe limit 6"
            res = graph.run(cypher).data()
            return {"code":10000,"msg":"查询成功","data":res}
        elif openid:
            # 根据用户id查询用户已经收藏的食谱
            print("根据用户id查询食谱和收藏关系")
            cypher = f"match (u:User)-[c:collect]->(r:Recipe) where u.openid = '{openid}' return r as recipe,coalesce(count(c)) as collect"
            res = graph.run(cypher).data()
            return {"code":10000,"msg":"查询成功","data":res}

    @marshal_with(response_fields)
    def post(self):
        #增加一个食谱记录

        args = parser.parse_args()

        print(args)
        task = {"name":"wuchuncheng","address":12}
        return task



api.add_resource(Recipe, '/recipe')



