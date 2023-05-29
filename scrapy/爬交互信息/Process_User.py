import requests
from bs4 import BeautifulSoup
import json

import model
from exts import session
from Parse_Url import parse_url
from Process_Recipe import process_recipe
def process_user(url):
    """
    爬取用户主页
    :param url: 用户主页URL
    :return: user_id || False
    """
    try:
        print("正在爬取",url,'的用户主页')
        userSoup = parse_url(url)
        # 获取user基本信息
        space_info = userSoup.find("div", {"class": 'space_wrap'})
        nickName = space_info.find("div", {"class": 'subname'}).find("a").text  # class=subname的div
        # avatarUrl = space_info.find("img",{"class": 'imgLoad'})['src']  # 用户隐私 不允许爬

        # 获取userID
        userID = ''
        user = model.UserModel.query.filter_by(nickName=nickName).first()
        if not user:
            user = model.UserModel(nickName=nickName)
            session.add(user)
            session.commit()
            print(f"\n该用户不存在于mysql中,已重新创建，用户信息：{nickName},user_id={user.id}")
        else:
            print(f"\n该用户已存在于mysql中，id={user.id}")
            return False

        userID = user.id

        # 获取所有食谱URL “下单交互关系”
        recipeUrlList = []
        big4_list = userSoup.find('div', {"class": "big4_list"}).find_all('li')
        recipeUrlList = [item.find('a')['href'] for item in big4_list]
        print(f"\n该用户主页所有食谱URL为{recipeUrlList[0:2]}...")
        # 挨个处理recipeUrl
        for recipeUrl in recipeUrlList:
            ingredientIDList = process_recipe(recipeUrl)  # 处理每一个食谱URL 返回对应主料 IDlist
            print(f"\n{recipeUrl}处理完毕，对应的食材URLLIST 为{ingredientIDList[0:2]}...")

            for item in ingredientIDList:
                # item和user_id添加下单关系
                interaction = model.User_IngredientModel.query.filter_by(user_id=userID,
                                                                         ingredient_id=item).first()  # 检查互动记录
                if not interaction:  # 若互动记录不存在
                    interaction = model.User_IngredientModel(user_id=userID, ingredient_id=item)
                    session.add(interaction)
                    session.commit()
                    print(f"\n{userID}和{item}的互动记录不存在，已重新创建互动记录，id={interaction.id}")

                else:
                    print(f"{userID}和{item}的互动记录已存在，id={interaction.id}")
                # 下单数量加1
                interaction.purchase_count = interaction.purchase_count + 1
                print(f"为{userID}和{item}添加下单关系")






        print(f"{userID} {nickName}的主页信息爬取完毕\n\n\n")


        # 收藏记录
        collections = model.CollectionModel.query.filter_by(user_id=userID)
        print(collections)
        print(f"共添加{len(collections)}条收藏记录，详情如下\n{collections}")
        # 交互记录
        interactions = model.User_IngredientModel.query.filter_by(user_id=userID)
        print(f"共添加{len(interactions)}条交互记录，详情如下\n{interactions}")

        return userID
    except Exception as e:
        session.rollback()
        print("process_user的错误",e)
        return None