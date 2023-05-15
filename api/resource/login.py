from flask_restful import Resource,Api,reqparse
from flask import Blueprint,current_app
from utils.neo4j import graph
import requests
from utils.process_token import setToken
bp = Blueprint("login",__name__)
api = Api(bp)
import model
from exts import session
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

        user = model.UserModel.query.filter_by(openid=openid).first()
        if user:
            return {"code": 10000, "msg": "注册成功", "data": {"token": token}}
        else:
            print("user不存在")
            try:
                user = model.UserModel(openid=openid, nickName="微信用户",
                                       avatarUrl="12412")
                session.add(user)
                session.commit()
                print("自动注册")
                return {"code": 10000, "msg": "自动注册成功", "data": {"token": token}}
            except Exception as e:
                print(e)
                return {"code": 10001, "msg": e, "data": {}}



api.add_resource(Login,"/login")
