import json
from py2neo import Graph
from gensim.models import Word2Vec
import numpy as np
from utils.neo4j import graph


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
                     vector_size=15,  # 词向量维数
                     sg=0,
                     min_count=3,
                     workers=20,
                     epochs=3000,  #
                     window=6,  # 使模型更关注单词的语义特征
                     )
    # 保存模型
    model.save("./训练结果/word2vec_cbow.model")

    return model


def ingredient_recommend_main(model, ingredient, target_num):
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
            new_ingredient = {'name': item, 'sim': model.wv.similarity(item, ingredient)}
            ingredients_recommend.append(new_ingredient)

    ingredients_recommend = sorted(ingredients_recommend, key=lambda ingredient: ingredient['sim'],
                                   reverse=True)  # 根据consine_sim对recommand_recipes降序排序
    rank = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # 各层次食材分布的数量
    for item in ingredients_recommend:
        if item['sim'] >= 0 and item['sim'] <= 0.1:
            rank[0] = rank[0] + 1
        elif item['sim'] > 0.1 and item['sim'] <= 0.2:
            rank[1] = rank[1] + 1
        elif item['sim'] > 0.2 and item['sim'] <= 0.3:
            rank[2] = rank[2] + 1
        elif item['sim'] > 0.3 and item['sim'] <= 0.4:
            rank[3] = rank[3] + 1
        elif item['sim'] > 0.4 and item['sim'] <= 0.5:
            rank[4] = rank[4] + 1
        elif item['sim'] > 0.5 and item['sim'] <= 0.6:
            rank[5] = rank[5] + 1
        elif item['sim'] > 0.6 and item['sim'] <= 0.7:
            rank[6] = rank[6] + 1
        elif item['sim'] > 0.7 and item['sim'] <= 0.8:
            rank[7] = rank[7] + 1
        elif item['sim'] > 0.8 and item['sim'] <= 0.9:
            rank[8] = rank[8] + 1
        elif item['sim'] > 0.9:
            rank[9] = rank[9] + 1
    print(rank)

    print(ingredients_recommend[0: rank[9] + rank[8]])


def verify_model(model):
    name_list = ["五花肉","带鱼", '方便面', '蒜蓉辣酱', '挂面', '牛奶', '鱿鱼', '豆腐', '黄瓜', '西兰花', '鸡蛋']
    for item in name_list:
        ingredient_recommend_main(model, item, 100)


def process_recipe(model):
    # 获取所有食谱id
    cypher = "match (r:Recipe) return r.id as id,r.name as rname"
    recipes = graph.run(cypher).data()
    vector_recipes = []
    for idx, recipe in enumerate(recipes):
        print(f"第{idx + 1}个食谱")
        # 查询每个食谱的对应食材名称
        id = recipe['id']
        # id = "3bf46e2f-09f6-4e0c-ba80-46e18dbd8bb0"
        cypher = f"match (r:Recipe) where r.id = '{id}' with r match (r)-[n:need]->(i:Ingredient) return n.type as type, i.name as name"
        res = graph.run(cypher).data()

        vecs = []  # 词向量数组
        weis = []  # 权值数组
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

        vector_recipes.append({"id": id, 'name': recipe['rname'], ''"vector": vectors_weighted_mean.tolist()})
    return vector_recipes


def process_store(vector_recipes):
    with open("./训练结果/vector_recipes_cbow.json", 'w') as f:
        json.dump(vector_recipes, f)
    print("食谱向量保存成功,请在static/json中替换原来的vector_recipes_cbow.json文件")


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
