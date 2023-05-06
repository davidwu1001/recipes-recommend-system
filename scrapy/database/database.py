import json
import time

from py2neo import Graph,NodeMatcher,RelationshipMatcher,Transaction
import uuid
from scrapy.chatgpt_.chatgpt import getRecipeSeasonAndArea

graph = Graph("bolt://localhost:7687", auth=("neo4j","11111111w"))
def generate_ID():
    return str(uuid.uuid4())

def Insert(category):
    """
    因为chatgpt的效果不固定，有时会生成死板的结果，比如每个季节都是固定四个地区，这样没有参考性
    可以通过观察第一个食材的结果，如果第一个结果表现良好，那么此次应该会成功
    :param category:
    :return:
    """
    tx = Transaction(graph)
    try:
        cate = category["category"]
        for sub in category['subcategories']:
            subcate = sub['subcategory'] #猪肉
            ingredients = sub['ingredients']
            for item in ingredients:
                # 先检查是否存在该结点,如果存在就跳过 这样能保证从断点开始，不用每次都从头开始
                cypher = f"match (n:Ingredient) where n.name = '{item}' return count(n) as exist"
                exist = graph.run(cypher).data()[0]['exist']
                print(item,exist)
                if exist == 0:  # 当不存在时才需要写数据
                    if category['category'] == "蔬菜" or category['category'] == "果品":  # 对蔬菜和果品添加时令和地区属性
                        season = getRecipeSeasonAndArea(item)
                        cypher = f"merge (i:Ingredient {{id:'{generate_ID()}',name:'{item}',category:'{cate}',subcategory:'{subcate}',spring:{season['spring']},summer:{season['summer']},autumn:{season['autumn']},winter:{season['winter']}}})"
                        time.sleep(20)  # 暂停20秒，解决openai api 3/m的限制
                    else:
                        cypher = f"merge (i:Ingredient {{id:'{generate_ID()}',name:'{item}',category:'{cate}',subcategory:'{subcate}'}})"
                    print(cypher)
                    graph.run(cypher)

        graph.commit(tx)
    except:
        graph.rollback(tx)
        raise
def main():
    """
    食材数据来源于ingredients.json，从美食天下网站上爬取下来的
    挨个插入到数据库中
    :return:
    """
    with open("../爬取结果/ingredients.json", 'r') as f:
        ingredients = json.load(f)
        for category in ingredients:
            Insert(category)
def Delete_all():
    cypher = "match ()-[n]->() delete n"
    graph.run(cypher)
    cypher = "match (n) delete n"
    graph.run(cypher)

if __name__ == "__main__":
    # Delete_all()  # 清空所有数据库
    main()



