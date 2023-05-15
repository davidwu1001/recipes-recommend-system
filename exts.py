from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db =SQLAlchemy()  # sqlalchemy实例对象，待与app绑定
session = db.session # session对象 线程安全，可以在线程之间共享
migrate = Migrate()  # 实例化Migreate

