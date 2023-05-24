from exts import db
from datetime import datetime
from flask_security import UserMixin, RoleMixin



class RecipeModel(db.Model):
    __tablename__ = "recipe"
    id = db.Column(db.String(200), primary_key=True)
    name = db.Column(db.String(200))
    picture = db.Column(db.String(500))
    category = db.Column(db.String(200))
    process = db.Column(db.String(200))
    text = db.Column(db.String(2000))
    time_consuming = db.Column(db.String(200))

    collections = db.relationship('CollectionModel', backref='recipe', lazy=True)


class IngredientModel(db.Model):

    """
    食材
    id name category subcategory spring summer autumn winter
    其中 id name 非空

    """

    __tablename__ = "ingredient"
    id = db.Column(db.String(200), primary_key=True)
    name = db.Column(db.String(200))
    category = db.Column(db.String(200))
    subcategory = db.Column(db.String(200))
    subcategory = db.Column(db.String(200))

    interactions = db.relationship('User_IngredientModel', backref='ingredient')

# role和user的多对多关系
roles_users = db.Table('roles_users',
                       db.Column('admin_id', db.Integer(), db.ForeignKey('admin.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class AdminModel(db.Model,UserMixin):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fs_uniquifier = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())

    roles = db.relationship('RoleModel', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


class RoleModel(db.Model, RoleMixin):
    __tablename__ = "role"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class UserModel(db.Model,UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nickName = db.Column(db.String(200), nullable=True)
    avatarUrl = db.Column(db.String(200), nullable=True)
    openid = db.Column(db.String(200), nullable=True, unique=True)

    interactions = db.relationship('User_IngredientModel', backref='user', lazy=True)
    orders = db.relationship('OrderModel', backref='create_user', lazy=True)
    collections = db.relationship('CollectionModel', backref='user', lazy=True)


class CollectionModel(db.Model):
    # 收藏关系
    __tablename__ = "collection"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.String(200), db.ForeignKey('recipe.id'), nullable=False)

# # role和user的多对多关系
order_item = db.Table('order_item',
                       db.Column('order_id', db.Integer(), db.ForeignKey('order.id')),
                       db.Column('ingredient_id', db.String(200), db.ForeignKey('ingredient.id')),
                       db.Column('quality',db.String(200))
                      )

# class Order_ItemModel(db.Model):
#     """
#     订单项目
#     id quality
#     外键： order_id ingredient_id
#     """
#     __tablename__ = "order_item"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#
#     ingredient_id = db.Column(db.String(200), db.ForeignKey('ingredient.id'), nullable=False)
#     order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)

class OrderModel(db.Model):
    # 订单
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    ingredients = db.relationship('IngredientModel',secondary=order_item,backref=db.backref('orders',lazy='dynamic'))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



class User_IngredientModel(db.Model):
    """
    用户-食材交互行为
    id, 浏览次数，是否收藏，下单次数
    外键：user_id,ingredient_id
    """
    __tablename__ = "user_ingredient"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    view_count = db.Column(db.Integer, default=0)
    is_favorite = db.Column(db.Boolean, default=False)
    purchase_count = db.Column(db.Integer, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ingredient_id = db.Column(db.String(200), db.ForeignKey('ingredient.id'), nullable=False)

