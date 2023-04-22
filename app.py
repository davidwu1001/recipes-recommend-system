import os
from flask import Flask,request
from flask_cors import CORS
import config
from api.resource.recipe import bp as recipe_bp
from api.resource.login import bp as login_bp
from api.resource.user import bp as user_bp
from api.resource.image import bp as image_bp
from api.resource.collection import bp as collection_bp
from api.resource.ingredient import bp as ingredient_bp
from utils.process_token import decodeToken

app = Flask(__name__)

app.config.from_object(config) #读入配置文件
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'media')
# api = Api(app)
CORS(app)
app.register_blueprint(recipe_bp)
app.register_blueprint(login_bp)
app.register_blueprint(user_bp)
app.register_blueprint(image_bp)
app.register_blueprint(collection_bp)
app.register_blueprint(ingredient_bp)

# init()
# api.add_resource(Recipe,'/')

@app.before_request
def before_request():
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
    app.run(debug=True,port=8001)

