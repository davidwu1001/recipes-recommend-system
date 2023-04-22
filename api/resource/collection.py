from flask_restful import Api,Resource,marshal_with,fields,reqparse
from flask import Blueprint,request
from utils.neo4j import graph

bp = Blueprint("collection", __name__)
api = Api(bp)

response_fields = {
    'msg': fields.String(default="无效响应"),
    'code': fields.Integer(default=9999),
}
recipe_fields = {
    'id':fields.String(attribute='recipe.id'),
    'name':fields.String(attribute='recipe.name'),
    'picture':fields.String(attribute='recipe.picture'),
    'time_consuming':fields.String(attribute='recipe.time_consuming'),
    'process':fields.String(attribute='recipe.process'),
    'category':fields.List(fields.String,attribute="recipe.category"),
}
response_fields['data'] = fields.List(fields.Nested(recipe_fields),default=[])

class Collection(Resource):
    @marshal_with(response_fields)
    def get(self):
        # 解析参数
        parser = reqparse.RequestParser()
        parser.add_argument("openid", type=str, location="args")
        args = parser.parse_args()
        openid = request.environ['openid']
        cpyher = f"match (n:User) where n.openid = '{openid}' with n match (n)-[r:collect]->(m:Recipe) return m as recipe"
        recipes = graph.run(cpyher).data()
        # 格式化响应
        return {"code": 10000,"msg":"查询成功","data":recipes}

    @marshal_with(response_fields)
    def post(self):
        # 解析参数
        parser = reqparse.RequestParser()
        parser.add_argument("openid", type=str,location="json")
        parser.add_argument("recipe_id", type=str,location="json")
        args = parser.parse_args()
        openid = request.environ['openid']
        print("openiddddddd=",openid)
        recipe_id = args.get("recipe_id")
        # 查询是否已经存在收藏关系
        cypher = f"match (u:User)-[r:collect]->(n:Recipe) where u.openid= '{openid}' and n.id = '{recipe_id}' return count(r) as exist"
        exist = graph.run(cypher).data()[0]['exist']
        print(exist)
        if not exist:
            # 添加收藏关系

            cypher = f"match (u:User), (r:Recipe) where u.openid = '{openid}' and r.id = '{recipe_id}' create (u)-[c:collect {{time:timestamp()}}]->(r) return c as collection"
            print(cypher)
            collection = graph.run(cypher).data()
            print(collection)
            if collection:
                return {"code": 10000,"msg":"收藏成功"}
            else:
                return {"code":10001,"msg":"收藏失败"}
        else:
            return {"code": 10002, "msg": "收藏失败！用户已收藏"}

    @marshal_with(response_fields)
    def delete(self):
        # 解析参数
        parser = reqparse.RequestParser()
        parser.add_argument("openid", type=str, location="json")
        parser.add_argument("recipe_id", type=str, location="json")
        args = parser.parse_args()
        openid = request.environ['openid']
        recipe_id = args.get("recipe_id")
        # 查询是否存在收藏关系
        cypher = f"match (u:User)-[r:collect]->(n:Recipe) where u.openid= '{openid}' and n.id = '{recipe_id}' return count(r) as exist"
        exist = graph.run(cypher).data()[0]['exist']
        print(exist)
        if exist:
            # 删掉收藏关系
            cypher = f"match (u:User)-[r:collect]->(n:Recipe) where u.openid= '{openid}' and n.id = '{recipe_id}' delete r"
            graph.run(cypher)
            return {"code": 10000, "msg": "取消收藏成功"}
        else:
            return {"code": 10002, "msg": "取消失败！用户还未收藏"}


api.add_resource(Collection,'/collection')
