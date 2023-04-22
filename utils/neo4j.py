from py2neo import Graph

# address = current_app.config["ADDRESS"]
# username = current_app.config["USERNAME"]
# password = current_app.config["PASSWORD"]
ADDRESS = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "11111111w"

graph = Graph(ADDRESS, auth=(USERNAME,PASSWORD))

