from app import app
from flask import current_app
import os
import json
import model
from gensim.models import Word2Vec
import scipy.spatial.distance as dist


def user_recommend_recipe(user, target_num):
    '''
    为用户推荐食谱
    :param user: object 包含id
    :param target_num: int 推荐的数量
    :return:
    '''
    # 读取食谱词向量
    vector_recipes = []
    path = os.path.join(current_app.root_path, 'static', 'json/vector_recipes.json')
    with open(path, 'r', encoding='utf-8') as f:
        # 读取食谱向量文件 todo 待爬完数据后重新计算
        vector_recipes = json.load(f)
    # 导入模型
    model_path = os.path.join(current_app.root_path, 'word2Vec', '训练结果/word2vec.model')
    word2vec = Word2Vec.load(model_path)
    # 所有食材词汇表
    vocab = word2vec.wv.key_to_index
    # 用户所有交互数据
    user = model.UserModel.query.filter_by(id=user[id]).first()
    interactions = user.interactions

    # 计算用户词向量
    weight_sum = 0  # 用于归一化
    user_vector = np.zeros(word2vec.vector_size)  # 初始化
    for interaction in interactions:
        # 每个交互数据食材Id
        ingredient_id = interaction.ingredient_id
        # 食材名称
        ingredient = model.IngredientModel.query.filter_by(id=ingredient_id).first()
        ingredient_name = ingredient.name
        if ingredient_name in word2vec.wv:
            # 词向量
            ingredient_vector = word2vec.wv[ingredient_name]
            # 交互数据
            purchase_count = interaction.purchase_count
            view_count = interaction.view_count
            collect_count = interaction.collect_count
            # 浏览 0.1 收藏 0.3 购买 0.6 分配权重
            weight = purchase_count * 0.1 + view_count * 0.3 + collect_count * 0.6
            weight_sum += weight
            user_vector += weight * ingredient_vector

    # 归一化
    user_vector /= weight_sum
    print("用户向量为", user_vector)
    print(len(user_vector))
    # 计算用户和所有食谱的余弦相似度
    recommend_recipes = []
    for vector_recipe in vector_recipes:
        vector = vector_recipe['vector']
        if len(vector)!=0:
            cosine_sim = 1 - dist.cosine(user_vector, vector)
            recommend_recipes.append({"id": vector_recipe['id'], 'name': vector_recipe['name'], "cosine_sim": cosine_sim})

    # 按照相似度排序
    recommend_recipes = sorted(recommend_recipes, key=lambda recipe: recipe['cosine_sim'], reverse=True)
    # 检查推荐食谱的对应余弦相似度
    for recipe in recommend_recipes[0:target_num]:
        print(recipe['name'], recipe['cosine_sim'])

    # 若target_num = 6 返回前6个食谱
    return recommend_recipes[0:target_num]


if __name__ == "__main__":
    with app.app_context():
        user_recommend_recipe(user={
            id: 124521566,
        }, target_num=6)


