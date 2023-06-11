from app import app
from flask import current_app
import os
import json
import model
from utils.neo4j import graph

cypher = 'match (n:Recipe)  unwind n.category as category return category, count(category) as count order by count DESC'
res = graph.run(cypher).data()
category_list = [{"value": 0, "text": "不限"}]
for idx,category in enumerate(res):
    if category['count'] > 100:
        category_list.append({"value": idx + 1, "text": category['category']})

print(category_list)
