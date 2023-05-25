from flask_restful import Resource,Api,reqparse,fields,marshal_with
from flask import Blueprint, request

import model
from utils.neo4j import graph
from model import UserModel
from exts import session
bp = Blueprint("user",__name__)
api = Api(bp)

user_parser = reqparse.RequestParser()
user_parser.add_argument("openid",type=str,location="json",help="openid不能为空")
user_parser.add_argument("nickName",location="json",help="姓名的格式错误")
user_parser.add_argument("avatarUrl",location="json",help="头像的url错误")

url_parser = reqparse.RequestParser()
url_parser.add_argument("tempUrl",type=str,location="args",help="没有URL")

user_fields = {
    "nickName":fields.String(attribute='nickName'),
    "avatarUrl":fields.String(attribute='avatarUrl'),
    "openid":fields.String(attribute='openid'),
}
response_fields = {
    'msg': fields.String(default="无效响应"),
    'code': fields.Integer(default=9999),
    "data": fields.Nested(user_fields)
}




response_fields['data'] = fields.Nested(user_fields,default="{}")
class User(Resource):
    @marshal_with(response_fields)
    def get(self):
        openid = request.environ['openid']

        user = model.UserModel.query.filter_by(openid=openid).first()
        return {"code": 10000, "msg": "查询用户信息成功", "data": user}

    @marshal_with(response_fields)
    def post(self):
        args = user_parser.parse_args();
        openid = request.environ['openid']
        nickName = args.get("nickName")
        avatarUrl = args.get("avatarUrl")
        print("昵称",nickName,avatarUrl)
        try:
            user = UserModel.query.filter_by(openid=openid).first()
            if nickName:
                user.nickName = nickName
            if avatarUrl:
                user.avatarUrl = avatarUrl
            session.commit()
            return {"code": 10000, "msg": "修改成功","data":user}
        except Exception as e:
            return {"code": 10001, "msg": "添加成功"+e, "data": user}











api.add_resource(User,"/user")
