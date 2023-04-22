import json

from py2neo import Graph,NodeMatcher,RelationshipMatcher,Transaction
import uuid
graph = Graph("bolt://localhost:7687", auth=("neo4j","11111111w"))
def generate_ID():
    return str(uuid.uuid4())

def Insert(category):
    tx = Transaction(graph)
    try:
        cate = category["category"]
        for sub in category['subcategories']:
            subcate = sub['subcategory'] #猪肉
            ingredients = sub['ingredients']
            for item in ingredients:
                item #里脊
                cypher = f"merge (i:Ingredient {{id:'{generate_ID()}',name:'{item}',category:'{cate}',subcategory:'{subcate}'}}) "
                graph.run(cypher)
        graph.commit(tx)

    except:
        tx.rollback()
        raise
def main():
    with open("../爬取结果/ingredients.json",'r') as f:
        ingredients = json.load(f)
        for category in ingredients:
            Insert(category)
def Delete_all():
    cypher = "match ()-[n]->() delete n"
    graph.run(cypher)
    cypher = "match (n) delete n"
    graph.run(cypher)
if __name__ == "__main__":
    Delete_all()
    main()


