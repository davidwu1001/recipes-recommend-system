from flask_restful import Resource,Api,reqparse,request
from flask import Blueprint,current_app
from utils.neo4j import graph
import requests
from utils.process_token import setToken
import model
bp = Blueprint("order",__name__)
api = Api(bp)
import model
from exts import session


parser = reqparse.RequestParser()
parser.add_argument("ingredientList",type=list,location='json')

class Order(Resource):

    def get(self):
        # 获取用户的所有订单信息
        openid = request.environ['openid']
        try:
            # 获取用户信息
            user = model.UserModel.query.filter_by(openid=openid).first()
            # 获取用户所有订单
            orders = user.orders
            orders_formed = []
            for order in orders:
                # 该订单所有食材
                ingredients = order.ingredients
                # 整合一下订单内容（所有食材的名称）到content属性中
                content = '，'.join([i.name for i in ingredients])
                orders_formed.append({"content":content,"date_created":order.date_created.strftime("%Y-%m-%d")})

            return {"code": 10000, "msg": "查询订单成功", "data": orders_formed}

            # 对每个订单整合一下内容
        except Exception as e:
            print(e)
            return {"code": 10001, "msg": "查询订单信息失败", "data": {}}
    def post(self):
        # 获取openid
        openid = request.environ['openid']
        # 获取格式化参数
        args = parser.parse_args()
        ingredientList = args.get('ingredientList')
        print(ingredientList)

        try:
            # 查询User_id
            user = model.UserModel.query.filter_by(openid=openid).first()
            user_id = user.id
            print("user_id",user_id)
            # 创建order记录 (user_id)
            order = model.OrderModel(user_id=user_id)
            session.add(order)
            session.commit()
            order_id = order.id
            print("order_id",order_id)
            # 创建order_item记录 order_id ingredient_id quality
            for ingredient in ingredientList:
                ingredient_id = ingredient['id']
                quality = ingredient['amount']
                order_item = model.order_item.insert().values(order_id=order_id, ingredient_id=ingredient_id, quality=quality)
                session.execute(order_item)

                # 查询有无交互记录 若有 则purchase_count+1 若无 则创建interaction记录（user_id,ingredient_id）
                interaction = model.User_IngredientModel.query.filter_by(user_id=user_id,
                                                                         ingredient_id=ingredient_id).first()
                if interaction:  # 交互记录存在
                    interaction.purchase_count = interaction.purchase_count + 1
                else:  # 交互记录不存在 直接创建
                    interaction = model.User_IngredientModel(user_id=user_id, ingredient_id=ingredient_id,
                                                             purchase_count=1)
                    session.add(interaction)
            session.commit()

            return {"code": 10000, "msg": "订单记录创建完成", "data": {}}
        except Exception as e:
            print(e)
            return {"code": 10001, "msg": "订单记录创建失败", "data": {}}


api.add_resource(Order, "/order")
