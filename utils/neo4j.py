from py2neo import Graph

# 开发环境
# ADDRESS = "bolt://localhost:7687"
# USERNAME = "neo4j"
# PASSWORD = "11111111w"

# 生产环境
ADDRESS = "bolt://49.233.27.20:7687"
USERNAME = "neo4j"
PASSWORD = "Wcc201001"

graph = Graph(ADDRESS, auth=(USERNAME,PASSWORD),name="recipe-knowledge-graph.db")

