from flask_restful import Resource,Api,reqparse
from flask import Blueprint,current_app
from utils.neo4j import graph
import requests
from utils.process_token import setToken
bp = Blueprint("login",__name__)
api = Api(bp)

class Login(Resource):
    def get(self):
        # 解析login接口登录参数
        login_parser = reqparse.RequestParser()
        login_parser.add_argument("code", type=str, location="args", help="code格式不对")
        args = login_parser.parse_args()
        code = args.get("code")
        # 请求微信接口
        params = {
            "appid": current_app.config["APPID"],
            "secret": current_app.config["APPSECRET"],
            "js_code": code,
            "grant_type": "authorization_code"
        }
        response = requests.get(url="https://api.weixin.qq.com/sns/jscode2session", params=params).json()
        openid = response["openid"]
        token = setToken(openid)
        # 查询数据库
        cypher = f"match (u:User) where u.openid = '{openid}' return u as user"
        res = graph.run(cypher).data()
        if res:
            code = 10000
            msg = "登录成功"
        else:
            cypher = f"create (u:User {{openid:'{openid}',nickName:'微信用户',avatarUrl:'data:image/png;base64,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'}})"
            graph.run(cypher)
            code = 10001
            msg = "您好，已自动注册"
        return {"code": code, "msg": msg, "data": {"token": token}}

api.add_resource(Login,"/login")
