import time

import requests
from bs4 import BeautifulSoup
from HandleSoup import handleSoup
import json
import random
import os
import urllib3

def handleUrl(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) App leWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53'
    }
    response = requests.get(url, verify=False, headers=headers)
    response.encoding = "utf-8"
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    return handleSoup(soup)
# 主函数
def handleRecipe(recipe_nums):
    recipes = [] #食谱对象容器
    #循环爬取食谱主页
    for item in recipe_nums:
        url = f"https://home.meishichina.com/recipe-{item}.html"
        print(url)
        recipe = handleUrl(url) #对于每一个url拿到食谱对象

        #url有效
        if recipe:
            recipes.append(recipe)


    store_json(recipes) # 加入到json
    store_txt(recipes) # 加入到语料库

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

if __name__ == '__main__':
    # 取消http警告
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    nums = list(range(100000, 999999))
    random_num = random.sample(nums, 10000) # 10000个随机序号
    for item in range(25): # 分25批爬取，每次间隔1分钟
        print(f"第{item+1}批正在爬取")
        start = item*400
        end = start + 400
        recipe_nums = random_num[start:end]
        handleRecipe(recipe_nums)
        print(f"第{item+1}批爬取完成，系统暂停30秒")
        time.sleep(30)

