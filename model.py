from exts import db
from datetime import datetime

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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200))
    category = db.Column(db.String(200))
    subcategory = db.Column(db.String(200))
    Areas = db.relationship("Ingredient_AreaModel", backref="ingredients")
    interactions = db.relationship('User_IngredientModel', backref='ingredient')

class UserModel(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nickName = db.Column(db.String(200), nullable=False)
    avatarUrl = db.Column(db.String(200), nullable=False)
    openid = db.Column(db.String(200), nullable=False, unique=True)

    interactions = db.relationship('User_IngredientModel', backref='user', lazy=True)
    orders = db.relationship('OrderModel', backref='create_user', lazy=True)
    collections = db.relationship('CollectionModel', backref='user', lazy=True)

class CollectionModel(db.Model):
    # 收藏关系
    __tablename__ = "collection"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.String(200), db.ForeignKey('recipe.id'), nullable=False)

class OrderModel(db.Model):
    # 订单
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    order_items = db.relationship('Order_ItemModel', backref='order', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Order_ItemModel(db.Model):
    """
    订单项目
    id quality
    外键： order_id ingredient_id
    """
    __tablename__ = "order_item"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quality = db.Column(db.String(200))

    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)


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
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)




class AreaModel(db.Model):
    """
    地区
    只有一个name主键

    """
    __tablename__ = "area"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200))


class Ingredient_AreaModel(db.Model):
    """
    食谱时令地区 多对多关系
    id Ingredient_id AreaModel season
    """
    __tablename__ = "ingredient_area"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    season = db.Column(db.String(200))

    Ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    Area_id = db.Column(db.Integer(), db.ForeignKey('area.id'), nullable=False)

