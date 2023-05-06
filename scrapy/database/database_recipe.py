import  json
from utils.escape import _escape,_unescape
from py2neo import Graph,NodeMatcher,RelationshipMatcher,Transaction
import uuid
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
        cypher = f"create (n:Recipe {{id:'{generate_ID()}',name:'{recipe['name']}',picture:'{picture}',time_consuming:'{time_consuming}',process:'{process}',category:{str(recipe['category'])},text:'{_escape(recipe['text'])}' }}) return n.id as id"
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

def main():
    with open("../爬取结果/recipes.json", 'r') as f:
        recipes = json.load(f)[1:]
        for recipe in recipes:
            Insert(recipe['recipe'],recipe['ingredient'],recipe['procedure'])


if __name__ == "__main__":
    main()

