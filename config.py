#使jsonify显示中文
JSON_AS_ASCII = False
# 密钥
SECRET_KEY = "skafkhfkafhkajsh"
BUNDLE_ERRORS = True

# 微信小程序
APPID = "wx861651342c75f407"
APPSECRET = "efd7471be381d96365821bbb4a811ba3"


# mysql开发环境
HOSTNAME = "127.0.0.1"
PORT = 3306
USERNAME = "root"
PASSWORD = "root"
DATABASE = "flask-admin-test"
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"

# mysql 生产环境
HOSTNAME = "49.233.27.20"
PORT = 3306
USERNAME = "root"
PASSWORD = "root"
DATABASE = "flask-admin-test"
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"


