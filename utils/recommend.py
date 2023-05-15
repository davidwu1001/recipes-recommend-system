import numpy
import scipy.spatial.distance as dist
from gensim.models import Word2Vec
from flask import current_app
import os
import json
from utils.neo4j import graph
def recommend_recipes(recipe, target_num):
    '''
    :param recipe: 食谱对象，要求包含id
    :param target_num: 推荐生成的食谱数量
    :return: 食谱id列表 列表中每个元素 {"id","name",""cosine_sim"}
    '''
    path = os.path.join(current_app.root_path, 'static', 'json/vector_recipes.json')
    with open(path, 'r', encoding='utf-8') as f:
        # 读取食谱向量文件 todo 换成由word2vec模型直接计算
        vector_recipes = json.load(f)

    for item in vector_recipes:
        # 查找recipe对应的向量
        if item['id'] == recipe['id']:
            recipe = item
            break

    # 构造生成的食谱列表
    recommend_recipes = []  # 推荐生成的食谱列表

    # 计算每一个食谱与recipe的余弦相似度
    for vector_recipe in vector_recipes:
        if vector_recipe['id'] != recipe['id']:  # 排序recipe本身
            cosine_sim = 1 - dist.cosine(vector_recipe['vector'], recipe['vector'])
            recommend_recipes.append(
                {"id": vector_recipe['id'], 'name': vector_recipe['name'], "cosine_sim": cosine_sim})
    # 根据consine_sim对recommand_recipes降序排序
    recommend_recipes = sorted(recommend_recipes, key=lambda recipe: recipe['cosine_sim'],
                               reverse=True)

    # 检查推荐食谱的对应余弦相似度
    for recipe in recommend_recipes[0:target_num]:
        print(recipe['name'], recipe['cosine_sim'])

    # 若target_num = 6 返回前6个食谱
    return recommend_recipes[0:target_num]


def ingredient_recommend_main(ingredient, target_num):
    '''
    食材 推荐 主料
    :param ingredient: 食材 要求包含name属性
    :param target_num: 推荐生成的数量
    :return: 推荐主料列表
    '''
    # 导入模型
    model_path = os.path.join(current_app.root_path, 'word2Vec', '训练结果/word2vec.model')
    model = Word2Vec.load(model_path)

    # 所有食材词汇表
    vocab = model.wv.key_to_index

    # 构造食材推荐列表
    ingredients_recommend = []

    # 计算  本食材 与所有其他食材的相似度
    for item in vocab:
        if item != ingredient['name']:  # 排除自己
            new_ingredient = {'name': item, 'sim': model.wv.similarity(item, ingredient['name'])}
            ingredients_recommend.append(new_ingredient)
    # 按照相似度 降序排序
    ingredients_recommend = sorted(ingredients_recommend, key=lambda ingredient: ingredient['sim'],
                                   reverse=True)

    # 若target_num = 6，取前6个推荐食材
    return ingredients_recommend[0:target_num]


def ingredient_recommend_recipe(ingredient, target_num):
    '''
    食材 推荐 食谱
    :param ingredient: 食材 要求包含name属性
    :param target_num: 推荐生成的数量
    :return: 推荐食谱列表
    '''
    # 读取word3vec模型
    model_path = os.path.join(current_app.root_path, 'word2Vec','训练结果/word2vec.model')
    model = Word2Vec.load(model_path)

    # 获取食材向量
    ingredient_vector = model.wv[ingredient['name']]

    # 读取食谱向量文件 todo 换成由word2vec模型直接计算
    path = os.path.join(current_app.root_path, 'static', 'json/vector_recipes.json')
    with open(path, 'r', encoding='utf-8') as f:
        vector_recipes = json.load(f)
    # 筛选食谱
    # cypher = f"match (r:Recipe)-[n:need]->(i:Ingredient) where i.name = '{ingredient['name']}' return r.id as id "
    # recipe_id_list = graph.run(cypher).data()  # 筛选后的食谱id
    #
    # print("recipe_list",recipe_id_list)
    #
    # # 构造 计算每一个符合要求的食谱的 词向量
    # vector_recipes_selected = []
    # for iitem in recipe_id_list:
    #     for item in vector_recipes: # 查找每一个id的食谱词向量
    #         if item['id'] == iitem['id']:
    #             vector_recipes_selected.append(item)
    #             break
    #
    # print("vector_recipes_selected",vector_recipes_selected)
    # # 推荐的食谱列表
    # recipes_recommend = []
    # # 食材依次与所有食谱求相似度
    # for recipe_vector in vector_recipes_selected:
    #     cosine_sim = 1 - dist.cosine(recipe_vector['vector'], ingredient_vector)  # 计算相似度
    #     new_recipe = {'id': recipe_vector['id'], 'name': recipe_vector['name'], 'sim': cosine_sim}
    #     recipes_recommend.append(new_recipe)

    # 构造推荐的食谱列表
    recommend_recipes = []
    print("食材向量=",ingredient_vector.shape,type(ingredient_vector))
    # 计算每一个食谱与recipe的余弦相似度
    for vector_recipe in vector_recipes:
        if len(vector_recipe['vector']) != 0:
            vector_recipe['vector'] = numpy.array(vector_recipe['vector'])  # list转化为numpt类型
            cosine_sim = 1 - dist.cosine(vector_recipe['vector'], ingredient_vector)
            recommend_recipes.append(
                {"id": vector_recipe['id'], 'name': vector_recipe['name'], "cosine_sim": cosine_sim})

    # 根据consine_sim对recommand_recipes降序排序
    recommend_recipes = sorted(recommend_recipes, key=lambda recipe: recipe['cosine_sim'],
                               reverse=True)

    # 检查推荐食谱的对应余弦相似度
    for recipe in recommend_recipes[0:target_num]:
        print(recipe['name'], recipe['cosine_sim'])

    # 若target_num = 6 返回前6个食谱
    return recommend_recipes[0:target_num]


