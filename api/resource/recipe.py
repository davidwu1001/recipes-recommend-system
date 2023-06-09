import json

from flask import Blueprint, request
from flask_restful import Resource,Api,reqparse,fields,marshal_with
from flask_paginate import Pagination
import model
from utils.neo4j import graph
from utils.recommend import recommend_recipes,ingredient_recommend_recipe,user_recommend_recipe
from exts import session
bp = Blueprint("recipe",__name__)
api = Api(bp)

parser = reqparse.RequestParser()
parser.add_argument("recipe_id",type=str,location="args",help="id不能为空")
parser.add_argument("name",type=str,location="args",help="姓名的格式错误")
parser.add_argument("season",type=str,location="args",help="季节的格式错误")
parser.add_argument("province",type=str,location="args",help="地区的格式错误")
parser.add_argument("category",type=str,location="args",help="菜品的格式错误")
parser.add_argument("openid",type= str,location="args",help="用户openid的格式错误")
parser.add_argument("location",type=str,location="args",help="location格式错误")
parser.add_argument("recommend_recipe_id",type= str,location="args",help="推荐食谱的id")
parser.add_argument("recommend_target_num",type= int,location="args",help="推荐生成的食谱个数")
parser.add_argument("recommend_ingredient_name",type= str,location="args",help="推荐食材的name")
parser.add_argument("page",type= int,location="args",help="当前页数")
parser.add_argument("per_page",type= int,location="args",help="每个多少个")

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
    'collect':fields.Integer(attribute='recipe.collect'),
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
        province = args.get("province")
        category = args.get("category")
        page = args.get("page")
        per_page = args.get("per_page")
        recommend_recipe_id = args.get("recommend_recipe_id")
        recommend_target_num = args.get("recommend_target_num")
        recommend_ingredient_name = args.get("recommend_ingredient_name")
        location = args.get("location")

        openid = request.environ['openid']
        user_id = request.environ['user_id']
        if recipe_id:
            #食谱详情
            print("食谱详情",recipe_id,openid)

            # neo4j中查询食谱信息
            cypher = f"match (r:Recipe)-[ne:need]->(i:Ingredient) where r.id = '{recipe_id}' with collect(i) as ingredients, r as recipe match (recipe)-[s:step]->(p:Procedure) with recipe,ingredients,collect(p) as procedures RETURN {{recipe: recipe, ingredients: ingredients, procedures: procedures}} AS recipe"
            recipe = graph.run(cypher).data()[0]['recipe']

            # 所有食谱
            ingredients =recipe['ingredients']
            # 交互记录
            for ingredient in ingredients:
                interaction = model.User_IngredientModel.query.filter_by(user_id=user_id,
                                                                         ingredient_id=ingredient['id']).first()
                if interaction:  # 存在
                    interaction.view_count = interaction.view_count + 1
                else:  # 不存在
                    interaction = model.User_IngredientModel(user_id=user_id, ingredient_id=ingredient['id'],
                                                             view_count=1)
                    session.add(interaction)
            session.commit()

            # mysql中查询收藏关系
            user = model.UserModel.query.filter_by(openid=openid).first()
            collect = model.CollectionModel.query.filter_by(user_id=user.id,recipe_id=recipe_id).first()
            recipe['recipe']['collect'] = (lambda c : 1 if collect  else 0)(collect)
            print(recipe['recipe'])


            return {"code":10000,"msg":"查询成功","data":[recipe]}
        elif recommend_recipe_id and recommend_target_num:  # 查询推荐食谱
            print("由食谱推荐食谱")
            recipes_recommend = recommend_recipes({"id":recommend_recipe_id},recommend_target_num)  # 调用util.recommend.recommend_recipes

            recipes_id_list = []  # 生成的推荐食谱id列表
            for recipe in recipes_recommend:
                recipes_id_list.append(recipe['id'])

            cypher = f'match (r:Recipe) where r.id in {str(recipes_id_list)} return r as recipe'
            res = graph.run(cypher).data()
            return {"code": 10000, "msg": "推荐生成完成", "data": res}
        elif recommend_ingredient_name:
            print("由食材推荐食谱")
            try:
                recipes_recommend = ingredient_recommend_recipe({'name':recommend_ingredient_name},recommend_target_num)  # 调用util.recommend.ingredient_recommend_recipe
            except Exception as e:
                return  {"code": 10001, "msg": "暂无推荐", "data": {}}
            recipes_id_list = []  #
            for recipe in recipes_recommend:
                recipes_id_list.append(recipe['id'])

            cypher = f"match (r:Recipe)-[n:need]->(i:Ingredient) where r.id in {str(recipes_id_list)} return distinct r as recipe limit 6"

            res = graph.run(cypher).data()
            return {"code": 10000, "msg": "推荐生成完成", "data": res}
        elif recommend_target_num:
            print("用户推荐食谱",user_id)
            # try:
            # 推荐食谱
            recipe_recommend = user_recommend_recipe(user={"id":user_id},target_num=recommend_target_num)
            # 食谱全部信息
            recipes = []
            for idx,recipe in enumerate(recipe_recommend):
                recipe_id = recipe['id']
                cypher = f"match (n:Recipe) where n.id = '{recipe_id}' return n as recipe"
                recipe = graph.run(cypher).data()[0]
                # 收藏关系
                collection = model.CollectionModel.query.filter_by(user_id=user_id,recipe_id=recipe_id).first()
                print(f"{user_id},{recipe_id}的收藏关系为{collection}")
                recipe['recipe']['collect'] = (lambda c:1 if c else 0)(collection)
                recipes.append(recipe)
            return {"code": 10000, "msg": "查询成功", "data": recipes}

            # except Exception as e:
                # return {"code": 10001, "msg": e, "data": {}}
        elif category:
            # 筛选条件
            print("筛选食谱",category,province,season,page,per_page,user_id)
            if category == "不限":
                if province and season:  # 有时令属性
                    print("有时令，无分类查询")
                    cypher = f"match (n:Recipe)-[ne:need]->(i:Ingredient) where ( n.name contains '{name}' or  exists(((:Ingredient {{name:'{name}'}})<-[:need]-(n)))) and ne.type = '主料' and '{province}' in i.{season} return n as recipe skip {(page - 1)*per_page} limit {per_page}"
                else:  # 无时令属性
                    print("无时令，无分类查询")
                    cypher = f"match (n:Recipe) where ( n.name contains '{name}' or  exists(((:Ingredient {{name:'{name}'}})<-[:need]-(n))))  return n as recipe skip {(page - 1)*per_page} limit {per_page}"
            else:
                if province and season:  # 有时令属性
                    print("有时令，有分类查询")
                    cypher = f"match (n:Recipe)-[ne:need]->(i:Ingredient) where ( n.name contains '{name}' or  exists(((:Ingredient {{name:'{name}'}})<-[:need]-(n))))  and '{category}' in n.category and ne.type = '主料' and '{province}' in i.{season} return n as recipe skip {(page - 1)*per_page} limit {per_page}"
                else:
                    print("无时令，有分类查询")
                    cypher = f"match (n:Recipe) where ( n.name contains '{name}' or  exists(((:Ingredient {{name:'{name}'}})<-[:need]-(n)))) and '{category}' in n.category return n as recipe skip {(page - 1)*per_page} limit {per_page}"
            recipes = graph.run(cypher).data()
            print(cypher)
            # 收藏关系
            for idx, recipe in enumerate(recipes):
                recipe_id = recipe['recipe']['id']
                collection = model.CollectionModel.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
                print(f"{user_id},{recipe_id}的收藏关系为{collection}")
                recipes[idx]['recipe']['collect'] = (lambda c: 1 if c else 0)(collection)



            return {"code":10000,"msg":"筛选结果是","data":recipes}
        elif location:
            # 时令食谱
            location = json.loads(location)
            province = location['province']
            season = location['season']
            print("时令食谱",province,season,page,per_page,user_id)
            # 食谱
            cypher = f"match (n:Recipe)-[ne:need]->(i:Ingredient) where '{province}' in i.{season} return n as recipe skip {(page - 1)*per_page} limit {per_page}"
            print(cypher)
            recipes = graph.run(cypher).data()
            print(recipes)
            # 收藏关系
            for idx,recipe in enumerate(recipes):
                recipe_id = recipe['recipe']['id']
                collection = model.CollectionModel.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
                print(f"{user_id},{recipe_id}的收藏关系为{collection}")
                recipes[idx]['recipe']['collect'] = (lambda c: 1 if c else 0)(collection)


            return {"code":10000,"msg":"查询成功","data":recipes}


    @marshal_with(response_fields)
    def post(self):
        #增加一个食谱记录

        args = parser.parse_args()

        print(args)
        task = {"name":"wuchuncheng","address":12}
        return task



api.add_resource(Recipe, '/recipe')



