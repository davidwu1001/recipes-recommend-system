import requests
from bs4 import BeautifulSoup
import json
from faker import Faker
fake = Faker()
import model
from exts import session
from Parse_Url import parse_url
from utils.neo4j import graph
from py2neo import Transaction
from utils.escape import _escape,_unescape
import uuid

def generate_ID():
    return str(uuid.uuid4())
def process_recipe(url):
    """
    处理食谱页面
    如果食谱已存在，就跳过存储操作 直接收藏
    :param url:
    :return: 食材idlist || False
    """
    soup = parse_url(url)
    if soup.find("img")['src'] == "//static.meishichina.com/v6/img/temp/404_1.png":
        # 网页不存在
        return False
    if not soup.find(id="recipe_title").text:  # 排除食谱名称为空
        #食谱不存在
        return False
    if not soup.find(id="recipe_De_imgBox"):
        #背景不存在
        return False

    # 获得用户信息
    username = soup.find("span",{"class":"userName"}).text
    user = model.UserModel.query.filter_by(nickName=username).first()
    print(f"\n处理食谱主页{url}\n该食谱的用户为{user.nickName}")
    # user一定存在
    def handleRecipe():
        recipe = {}
        # 食谱名称
        recipe['name'] = soup.find(id="recipe_title").text
        # 食谱工艺
        if soup.find("span", string="工艺"):
            recipe['process'] = soup.find("span", string="工艺").findParent("li").find("a").text

        # 食谱耗时
        if soup.find("span", string="耗时"):
            recipe['time_consuming'] = soup.find("span", string="耗时").findParent("li").find("a").text

        #食谱口味
        if soup.find("span", string="口味"):
            recipe['taste'] = soup.find("span", string="口味").findParent("li").find("a").text

        # 食谱难度
        if soup.find("span", string="难度"):
            recipe['difficulty'] = soup.find("span", string="难度").findParent("li").find("a").text

        # 食谱背景图片
        recipe['picture'] = soup.find(id="recipe_De_imgBox").find("img")['src']

        # 食谱说明
        if soup.find(id="block_txt1"):
            recipe['text'] = soup.find(id="block_txt1").text
        else:
            recipe['text'] = ""

        #食谱类别
        recipe['category'] = []
        cates = soup.find_all("a", {'class': "vest"})
        for cate in cates:
            recipe['category'].append(cate.text)
        return recipe

    def handleIngredients():
        ingredients = []

        fieldset = soup.find_all("fieldset", {"class": "particulars"})
        for index, item in enumerate(fieldset):
            type = item.find("legend").text
            for iitem in item.find_all("li"):
                ingredient = {}
                ingredient["name"] = iitem.find('b').text
                ingredient["amount"] = iitem.find("span", {"class": "category_s2"}).text
                ingredient["type"] = type
                ingredient["seq"] = index + 1
                ingredients.append(ingredient)
        return ingredients

    def handleProcedures():
        procedures = []

        recipeStep = soup.find("div", {"class": 'recipeStep'}).find_all("li")
        for index, item in enumerate(recipeStep):
            procedure = {}
            if item.find("img"):
                procedure['picture'] = item.find("img")['src']
            else:
                procedure['picture'] = ""

            procedure['text'] = item.find('div', {'class': "recipeStep_word"}).get_text('/')
            procedure['text'] = procedure['text'][
                                procedure['text'].find('/') + 1:]  # 为了去掉“1/准备好各种材料。配菜的尖椒、洋葱也可以用彩椒代替”。前面的数字
            procedure['seq'] = item.find('div', {'class': "recipeStep_num"}).text
            procedures.append(procedure)
        return procedures

    recipe = handleRecipe()
    procedure = handleProcedures()
    ingredient = handleIngredients()
    print(f"\n食谱信息为{recipe}")
    # database
    res = Insert_neo4j(recipe=recipe, ingredients=ingredient, procedures=procedure)  # neo4j
    ingredientIDList = Insert_mysql(recipe=recipe, ingredients=ingredient)  # mysql


    print("\n\n现在开始寻找收藏关系")
    # “你可能会喜欢”部分，“收藏”关系
    # case1 专题+食谱
    # case2 纯食谱
    collect_list = soup.find('div', {"class": "left3_list"}).find_all("li")

    for item in collect_list:
        # 先判断是专题连接还是食谱连接
        if item.find("span"):  # 是专题
            theme_url = item.find('a')['href']
            theme_name = item.find("p").text
            print(f"发现专题{theme_name},url为{theme_url}")
        else:
            recipe_url = item.find("a")['href']
            recipe_name = item.find("p").text
            print(f"发现食谱 {recipe_name}, url为{recipe_url}")
            # 所有食材
            cypher = f"match (n:Recipe)-[ne:need]->(i:Ingredient) where n.name = '{recipe_name}' return i as ingredient"
            res = graph.run(cypher).data()
            if res:  # 食谱存在
                print(f"收藏操作时，{recipe_name}在neo4j中存在, 食材id列表为{res[0:2]},准备为用户和食材添加收藏关系")
                for item in res:

                    # 食材在mysql中是否存在
                    ing = model.IngredientModel.query.filter_by(id=item["ingredient"]['id']).first()
                    if not ing:  # 存在
                        ing = model.IngredientModel(id=item["ingredient"]['id'],name=item["ingredient"]['name'])
                        session.add(ing)
                        session.commit()
                        print(f"{item['ingredient']['name']}在mysql中不存在,但是已经创建，id为{item['ingredient']['id']}")
                    # 判断item和user.id之间有无互动关系
                    item = item['ingredient']['id']

                    print(f"\n现在开始创建收藏关系")
                    # 创建collection记录
                    collection = model.CollectionModel.query.filter_by(user_id=user.id,recipe_id=recipe['id']).first()
                    if not collection:  # 收藏记录不存在
                        collection = model.CollectionModel(user_id=user.id,recipe_id=recipe['id'])
                        session.add(collection)
                        session.commit()
                        print(f"{user.id},{recipe['id']}collection记录不存在，已生成 id为{collection.id}")
                    else:
                        print(f"{user.id},{recipe['id']}collection记录已存在,id为{collection.id}")
                    print(f"\n现在开始添加互动记录")
                    interaction = model.User_IngredientModel.query.filter_by(user_id=user.id,
                                                                             ingredient_id=item).first()
                    if interaction:  # 记录存在
                        # 创建收藏关系
                        interaction.collect_count = interaction.collect_count + 1
                        print(f"{interaction.user_id}和{interaction.ingredient_id}的互动记录存在并已更新，id为{interaction.id}")
                    else:  # 交互记录不存在
                        interaction = model.User_IngredientModel(user_id=user.id,ingredient_id=item,collect_count=1)
                        session.add(interaction)
                        session.commit()
                        print(f"{interaction.user_id}和{interaction.ingredient_id}的互动记录不存在，已重新创建，id为{interaction.id}")
            else:
                print("该食谱在mysql数据库中不存在")



    return ingredientIDList
def Insert_neo4j(recipe,ingredients,procedures):
    tx = Transaction(graph)
    try:
        # 先检查该食谱是否已存在
        cypher = f"match (r:Recipe) where r.name = '{recipe['name']}' return r limit 1"
        r = graph.run(cypher).data()
        if r:
            r = r[0]['r']
            print(f"\n{recipe['name']}在neo4j中已存在，id={r['id']}")
            recipe_id = r['id']
        else:
            if "picture" in recipe:
                picture = recipe["picture"]
            else:
                picture = ''
            if "time_consuming" in recipe:
                time_consuming = recipe["time_consuming"]
            else:
                time_consuming = ''
            if "process" in recipe:
                process = recipe["process"]
            else:
                process = ''

            cypher = f"create (n:Recipe {{id:'{generate_ID()}',name:'{_escape(recipe['name'])}',picture:'{picture}',time_consuming:'{time_consuming}',process:'{process}',category:{str(recipe['category'])},text:'{_escape(recipe['text'])}' }}) return n.id as id"
            recipe_id = tx.run(cypher).evaluate("id")
            print(f"\n在neo4j中{recipe['name']}不存在，已重新创建记录，id={recipe_id}\n")


        for ingredient in ingredients:
            # 先找有没有已知的食材结点
            cypher = f"match (i:Ingredient) where i.name = '{ingredient['name']}' return i.id as id"
            res = graph.run(cypher).data()
            if res:
                # 存在就用存在的那个id
                ingredient_id = res[0]['id']

            else:
                #不存在 就重新创建一个食材结点
                    cypher = f"merge (i:Ingredient {{id:'{generate_ID()}',name:'{ingredient['name']}'}}) return i.id as id"
                    ingredient_id = tx.run(cypher).evaluate('id')

            cypher = f"match (r:Recipe),(i:Ingredient) where r.id= '{recipe_id}' and i.id = '{ingredient_id}' create (r)-[n:need {{id:'{generate_ID()}',amount:'{ingredient['amount']}',type:'{ingredient['type']}',seq:'{ingredient['seq']}'}}]->(i)"
            tx.run(cypher)

        for procedure in procedures:
            cypher = f"merge (p:Procedure {{id:'{generate_ID()}',picture:'{procedure['picture']}',text:'{_escape(procedure['text'])}',seq:'{procedure['seq']}'}})  return p.id as id"
            procedure_id = tx.run(cypher).evaluate("id")
            cypher = f"match (r:Recipe),(p:Procedure) where r.id = '{recipe_id}' and p.id = '{procedure_id}' create (r)-[s:step {{id:'{generate_ID()}'}}]->(p)"
            tx.run(cypher)

        graph.commit(tx)

        cypher = "match (n:Recipe) return count(n) as num"
        num = graph.run(cypher).data()[0]['num']
        print(f"当前recipes总数{num}个")

        return True
    except Exception as e:
        tx.rollback()
        print("Insert_neo4j",e)
        raise
        return False

def Insert_mysql(recipe,ingredients):
    """
    将食谱记录插入到mysql中，返回对应食材IdList
    :param recipe:
    :param ingredients:
    :return: 食材idlisrt || []
    """
    try:
        # 从neo4j中查找recipe_id
        cypher = f"match (n:Recipe) where n.name='{recipe['name']}' return n.id as id"
        recipe_id = graph.run(cypher).data()[0]['id']
        recipe['id'] = recipe_id

        print(f"\n现在将{recipe['name']}插入到mysql")
        # 判断食谱在mysql是否存在
        _recipe = model.RecipeModel.query.filter_by(name=recipe['name']).first()
        if not _recipe:  # 食谱不存在
            recipe['category'] = '，'.join(recipe['category'])  # 目录一开始是数组类型，转化为字符串
            _recipe = model.RecipeModel(id=recipe['id'],name=_escape(recipe['name']),picture=recipe['picture'],category=recipe['category'],process=recipe['process'],text=_escape(recipe['text']),time_consuming=recipe['time_consuming'])
            session.add(_recipe)
            session.commit()
            print(f"{recipe['name']}在mysql中不存在，已重新创建记录，id是{_recipe.id}]\n")
        else:
            print(f"{recipe['name']}在mysql中已存在，id={recipe['id']}\n")


        ingredientIDList = []
        # 处理食材
        for item in ingredients:
            ingredient = model.IngredientModel.query.filter_by(name=item['name']).first()
            if not ingredient:
                ingredient = model.IngredientModel(id=generate_ID(),name=item['name'])
                session.add(ingredient)
                session.commit()
                print(f"{ingredient.name}在mysql中不存在，已重新创建记录,id={ingredient.id}")
            else:
                print(f"{ingredient.name}在mysql中已存在,id={ingredient.id}")
            # 将新添加的食材id加入list
            ingredientIDList.append(ingredient.id)

        session.commit()

        num = model.RecipeModel.query.count()
        print(f"\n\nmysql recipe当前{num}个")

        return ingredientIDList
    except Exception as e:
        print(e)
        session.rollback()
        print(f"\nmysql上传失败")
        return []