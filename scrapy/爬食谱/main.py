import time

import requests
from bs4 import BeautifulSoup
from HandleSoup import handleSoup
import json
import random
import os
import urllib3
from faker import Faker
fake = Faker()
def handleUrl(url):
    # 使用faker随机生成user-agent用于反反爬虫
    headers = {
        'User-Agent': fake.user_agent(),
        'Referer': fake.url(),
        'Cookie': fake.uuid4()
    }

    # 排除代理错误的情况 也就是被美食天下ban了
    try:
        response = requests.get(url, verify=False, headers=headers)
        response.encoding = "utf-8"
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        return handleSoup(soup)
    except requests.exceptions.ProxyError as e:
        print("代理错误：", e)
        return {}
        # 处理代理错误的情况
    except requests.exceptions.RequestException as e:
        print("请求错误：", e)
        return {}
# 主函数
def handleRecipe(recipe_nums):
    recipes = []  # 新添加到食谱
    #循环爬取食谱主页
    for idx,item in enumerate(recipe_nums):
        url = f"https://home.meishichina.com/recipe-{item}.html"
        recipe = handleUrl(url) #对于每一个url拿到食谱对象

        #url有效
        if recipe:
            recipes.append(recipe)
            print(f"{idx} {recipe['recipe']['name']}")


    store_json(recipes) # 加入到json
    store_txt(recipes) # 加入到语料库
    return len(recipes)

def store_json(recipes):
    #将json字符串写入文件
    with open("../爬取结果/recipes.json",'r+') as f:
        file_size = os.path.getsize("../爬取结果/recipes.json")
        if file_size == 0:
            #文件为空 设置为空数组
            old_recipes = []
        else:
            #文件不空
            old_recipes = json.load(f)

        recipes = recipes + old_recipes

        # 将python对象转化为json字符串
        json_str = json.dumps(recipes)
        #清空文件
        f.seek(0)
        f.truncate(0)
        #写入新的文件
        f.write(json_str)
        print(f"食谱数据已写入recipes.json中,本次添加{len(recipes)-len(old_recipes)}个，共{len(recipes)}个")

def store_txt(recipes):
    with open("../爬取结果/recipes.txt",'r+',encoding="utf-8") as f:
        # 处理旧数据
        num = 0
        file_size = os.path.getsize("../爬取结果/recipes.txt")
        old_recipes = []
        if file_size != 0:
            lines = f.readlines()
            for line in lines:
                num = num + 1
                old_recipes.append(line.strip())
        # 加入新的数据
        for recipe in recipes:
            num = num + 1
            new_line = "" # 新的预料记录
            for ingredient in recipe['ingredient']: # 只将食材信息加入预料记录
                new_line = new_line + ' ' + ingredient['name']
            f.write(new_line+"\n")
        print(f"已写入语料库，目前语料库共有{num}条记录")
def get_state():
    with open("state.json", 'r+', encoding="utf-8") as f:
        f.seek(0)
        state = json.load(f)
        return state
def set_state(current_group,total_recipe_num):
    with open("state.json", 'w') as f:
        f.write(json.dumps({"current_group":current_group,"total_recipe_num":total_recipe_num}))
def get_random_num(current_group):
    with open("random_num.json",'r+') as f:
        f.seek(0)
        random_nums = json.load(f)
        return random_nums[current_group]
if __name__ == '__main__':
    # 取消http警告
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    while True:
        # 获取当前状态，读取到了那一组
        state = get_state()
        current_group = state['current_group']   # 当前读到了那一组
        total_recipe_num = state['total_recipe_num']  # 目前爬取的recipe总数

        random_nums = get_random_num(current_group)  # 400个随机序号

        len_new = handleRecipe(random_nums)  # 返回新生成的食谱数量

        current_group = current_group + 1
        total_recipe_num = total_recipe_num + len_new
        set_state(current_group,total_recipe_num)

        if total_recipe_num >= 10000:  # 一万个食谱，之后结束爬取
            break


        print(f"第{current_group}批爬取完成，系统暂停20秒")
        time.sleep(30)


