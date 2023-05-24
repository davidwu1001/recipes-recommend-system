import os
from flask import Flask,request
from flask_cors import CORS
import config
from api.resource import recipe,login,user,image, collection,ingredient,order
from utils.process_token import decodeToken
from exts import db, migrate  # 插件

# 创建app实例
app = Flask(__name__)
# 读入配置文件
app.config.from_object(config)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'media')  # todo 将服务放到服务器上，使用服务器的静态文件地址
# 允许跨域请求
CORS(app)
# db绑定app
db.init_app(app)
# migrate绑定app,db
migrate.init_app(app, db)

app.register_blueprint(recipe.bp)
app.register_blueprint(login.bp)
app.register_blueprint(user.bp)
app.register_blueprint(image.bp)
app.register_blueprint(collection.bp)
app.register_blueprint(ingredient.bp)
app.register_blueprint(order.bp)

# init()
# api.add_resource(Recipe,'/')

@app.before_request
def before_request():
    """
    检查token
    :return:
    """
    white_list = ['login.login','image.image']
    print("endpoint=",request.endpoint)

    #login请求不需要验证身份
    if request.endpoint in white_list:
        return

    token = request.headers.get("Authorization")
    verify = decodeToken(token)
    if type(verify) == str:
        # token验证不成功 返回错误信息
        return {"message":verify}, 401
    else:
        # token 验证成功 拿到openid
        openid = verify['openid']
        request.environ['openid'] = openid


if __name__ == '__main__':
    print(app.debug)
    app.run(debug=True,port=8001)

