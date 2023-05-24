import  json
from utils.escape import _escape,_unescape
import uuid
from py2neo import Graph,NodeMatcher,RelationshipMatcher,Transaction

graph = Graph("bolt://localhost:7687", auth=("neo4j","11111111w"))
def generate_ID():
    return str(uuid.uuid4())
def Delete_all():
    cypher = "match ()-[n]->() delete n"
    graph.run(cypher)
    cypher = "match (n) delete n"
    graph.run(cypher)
def Insert(recipe,ingredients,procedures):
    tx = Transaction(graph)
    try:
        # 先检查该食谱是否已存在
        cypher = f"match (r:Recipe) where r.name = '{recipe['name']}' return count(r) as exist"
        exist = graph.run(cypher).data()[0]['exist']
        if exist:
            print(f"{recipe['name']}已存在")
            return
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

    except:
        tx.rollback()
        raise
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

def main():
    with open("../爬取结果/recipes.json", 'r') as f:
        recipes = json.load(f)[1:]

        recipes = dataWashing(recipes)  # 数据清洗

        for idx,recipe in enumerate(recipes):
            print(f"插入{idx} {recipe['recipe']['name']}")
            Insert(recipe['recipe'],recipe['ingredient'],recipe['procedure'])


if __name__ == "__main__":
    main()

