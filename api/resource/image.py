from flask_restful import Resource,Api,reqparse,fields,marshal_with
from flask import Blueprint,current_app,request
from werkzeug.datastructures import FileStorage
from utils.img_upload import img_upload
import requests
bp = Blueprint("image",__name__)
api = Api(bp)

response_fields = {
    'msg': fields.String(default="无效响应"),
    'code': fields.Integer(default=10000)
}

response_fields['data'] = {}
response_fields['data']['imageUrl'] = fields.String

class Image(Resource):
    @marshal_with(response_fields)
    def post(self):
        # 上传图片到本地
        parser = reqparse.RequestParser()
        parser.add_argument("image",type=FileStorage,location="files",help="图片错误")
        args = parser.parse_args()

        image = args.get("image")
        print(image)
        img = img_upload(image)
        print(img)
        if img == None:
            return {"code":10001,"msg":"图片格式有误"}
        else:
            img_path = img["img_path"]
            print(img_path)
            return {"code":10000,"msg":"上传成功","imageUrl":img_path}

    def get(self):
        res = requests.get("http://tmp/Cg2CoSgMuTK6c50bf72e3e9b0247869cb3aba8c4dd12.jpeg")
        return res

api.add_resource(Image, "/image")