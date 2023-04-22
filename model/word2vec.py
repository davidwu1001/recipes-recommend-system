import json
from py2neo import Graph
from gensim.models import Word2Vec
import numpy as np
ADDRESS = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "11111111w"

graph = Graph(ADDRESS, auth=(USERNAME, PASSWORD))


def process_file(file):
    # 读数据
    filtered_tokens = []
    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            filtered_tokens.append(line.split())

    return filtered_tokens


def process_corpus(file):
    # 处理数据
    tokenized_corpus = process_file(file)
    # 训练Word2Vec模型
    model = Word2Vec(sentences=tokenized_corpus,
                     vector_size=50,
                     sg=1,
                     min_count=1,
                     workers=4,
                     epochs=5,  # 防止过拟合
                     window=7,  # 使模型更关注单词的语义特征
                     )
    # 保存模型
    model.save("./训练结果/word2vec.model")



    return model
def ingredient_recommend_main(model,ingredient, target_num):
    '''
    食材 推荐 主料
    :param ingredient: 食材 要求包含name属性
    :param target_num: 推荐生成的数量
    :return: 推荐主料列表
    '''
    print(ingredient)
    vocab = model.wv.index_to_key  # 所有食材词汇表
    ingredients_recommend = []  # 食材推荐列表
    for item in vocab:  # 计算ingredient与所有其他食材的相似度
        if item != ingredient:  # 排除自己
            new_ingredient = {'name':item,'sim':model.wv.similarity(item,ingredient)}
            ingredients_recommend.append(new_ingredient)
    ingredients_recommend = sorted(ingredients_recommend, key=lambda ingredient: ingredient['sim'],
                               reverse=True)  # 根据consine_sim对recommand_recipes降序排序
    print(ingredients_recommend[0:target_num])


def verify_model(model):
    name_list = ["带鱼",'红烧肉','方便面','蒜蓉辣酱','挂面','牛奶','鱿鱼','豆腐']
    for item in name_list:
        ingredient_recommend_main(model,item,6)


def process_recipe(model):
    # 获取所有食谱id
    cypher = "match (r:Recipe) return r.id as id,r.name as rname"
    recipes = graph.run(cypher).data()
    vector_recipes = []
    for idx,recipe in enumerate(recipes):
        print(f"第{idx+1}个食谱")
        # 查询每个食谱的对应食材名称
        id = recipe['id']
        # id = "3bf46e2f-09f6-4e0c-ba80-46e18dbd8bb0"
        cypher = f"match (r:Recipe) where r.id = '{id}' with r match (r)-[n:need]->(i:Ingredient) return n.type as type, i.name as name"
        res = graph.run(cypher).data()

        vecs = [] # 词向量数组
        weis = [] # 权值数组
        for item in res:
            # 查询每一个食材的词向量
            if item['name'] in model.wv:
                # 词向量存在
                vector = model.wv[item['name']]
                # print(item['type'])
                vecs.append(vector)
                if item['type'] == "主料":
                    # 主料权值设置为10
                    weis.append(10)
                elif item['type'] == "辅料":
                    # 辅料权值设置为7
                    weis.append(7)
                else:
                    # 配料权值设置为4
                    weis.append(4)


        # 转化为np类型
        vectors = np.array(vecs)
        weights = np.array(weis)
        # 归一化权值
        normalized_weights = weights / np.sum(weights)
        # 计算加权平均和
        vectors_weighted_mean = np.sum(vectors * normalized_weights[:, None], axis=0)
        vector_recipes.append({"id":id,'name':recipe['rname'],''"vector":vectors_weighted_mean.tolist()})
    return vector_recipes
def process_store(vector_recipes):
    with open("./训练结果/vector_recipes.json", 'w') as f:
        json.dump(vector_recipes, f)
    print("食谱向量保存成功")

if __name__ == "__main__":
    file = "./语料库/recipes.txt"
    # word2Vec训练模型 为每个单词生成向量
    model = process_corpus(file)

    # 验证模型
    verify_model(model)
    # 处理每一个食谱
    vector_recipes = process_recipe(model)
    # 将训练结果存储到文件中
    process_store(vector_recipes)
