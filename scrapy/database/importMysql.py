import model
from exts import session
from model import UserModel,RecipeModel,IngredientModel
import json
from utils.neo4j import graph
from app import app
def Insert_Recipe(recipe):
    with app.app_context():  # 在应用上下文中进行
        try:
            session.begin()
            # todo 检查用户是否存在 若不存在先创建这个用户
            # 判断该食谱是否已存在
            exist = RecipeModel.query.filter_by(name=recipe['name']).first()
            if not exist:
                print(f"插入{recipe['name']}")
                recipe['category'] = '，'.join(recipe['category'])  # 目录一开始是数组类型，转化为字符串 todo 将category单独成为一个表
                _recipe = RecipeModel(**recipe)  # 将字典转化为类
                session.add(_recipe)
            session.commit()
        except Exception as e:
            # 回滚事务
            session.rollback()
            print("数据库出错了",e)
def Insert_Ingredient(category):
    with app.app_context():  # 在应用上下文中进行
        try:
            session.begin()
            cate = category["category"]
            for sub in category['subcategories']:
                subcate = sub['subcategory']  # 猪肉
                ingredients = sub['ingredients']
                for item in ingredients:  # name
                    # 先检查是否存在该结点,如果存在就跳过 这样能保证从断点开始，不用每次都从头开始
                    exist = IngredientModel.query.filter_by(name=item).first()
                    if not exist:  # 食材不存在
                        _ingredient = IngredientModel(name=item, category=cate, subcategory=subcate)
                        print(f"插入{_ingredient.name}")
                        session.add(_ingredient)
            session.commit()
        except Exception as e:
            # 回滚事务
            session.rollback()
            print("数据库出错了",e)
def dataWashing(recipes):
    """
    清洗数据
    :param recipes:
    :return:
    """
    old_num = len(recipes)
    for recipe in recipes:
        if not recipe['recipe']['name']:  # 清洗掉不存在的食谱
            recipes.remove(recipe)
        if len(recipe['recipe']['name']) > 10:  # 清洗名字太长的数据
            recipes.remove(recipe)
    new_num = len(recipes)
    print(f"数据清洗完成，清洗前{old_num}，清理后{new_num}，共清洗掉{old_num-new_num}条无效数据")
    return recipes

def handlerRecipe():
    # 从neo4j中查询食谱插入 保证 recipe的id一致
    cypher = "match (n:Recipe) return n as recipe"
    recipes = graph.run(cypher).data()
    for idx, recipe in enumerate(recipes):
        # print(f"插入{idx} {recipe['recipe']['name']}")
        Insert_Recipe(recipe['recipe'])

def handleIngredient():
    with open("source/ingredients.json") as f:
        ingredients = json.load(f)
        for category in ingredients:
            Insert_Ingredient(category)


def syncIngredientID():
    # 获取neo4j中的所有食材
    cypher = "match (n:Ingredient) return n as ingredient"
    ingredients_neo4j = graph.run(cypher).data()

    # mysql中食材清空 <- 先把用户信息和交互信息都删了 done

    # 循环全部添加到mysql中
    count = 0
    for ingredient_neo4j in ingredients_neo4j:
        ingredient_neo4j = ingredient_neo4j['ingredient']  # 截取

        ingredient_mysql = model.IngredientModel(id=ingredient_neo4j['id'],name=ingredient_neo4j['name'],category=ingredient_neo4j['category'],subcategory=ingredient_neo4j['subcategory'])
        session.add(ingredient_mysql)
        count = count + 1
    session.commit()
    print(count)

if __name__ == "__main__":
    with app.app_context():
        pass
        # syncIngredientID()
    # handleIngredient()