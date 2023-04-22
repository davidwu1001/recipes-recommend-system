import requests
from bs4 import BeautifulSoup
from HandleSoup import handleSoup
import json
def handleUrl(url):

    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) App leWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53'
    }
    response = requests.get(url, verify=False, headers=headers)
    response.encoding = "utf-8"
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')


    return handleSoup(soup,url) # 每一个url对应一个食材大类 比如肉禽类


def handleIngredients():
    url_list = [
        "https://www.meishichina.com/YuanLiao/category/rql/",
        "https://www.meishichina.com/YuanLiao/category/scl/",
        "https://www.meishichina.com/YuanLiao/category/shucailei/",
        "https://www.meishichina.com/YuanLiao/category/guopinlei/",
        "https://www.meishichina.com/YuanLiao/category/mmdr/",
        "https://www.meishichina.com/YuanLiao/category/tiaoweipinl/",
        "https://www.meishichina.com/YuanLiao/category/yaoshiqita/"
    ]
    ingredients = [] # 最终的食材数据

    for item in url_list:
        url = item
        category = handleUrl(url) # 大类
        ingredients.append(category)
    print("食材对象组装完成")
    store(ingredients)

def store(ingredients):
    # 将字典对象转换为JSON字符串
    json_str = json.dumps(ingredients)

    # 将JSON字符串写入文件，编码设置为UTF-8
    with open("../爬取结果/ingredients.json", 'w') as f:
        f.write(json_str)
    print("食材数据存储至ingredients.json中")

if __name__ == '__main__':
    handleIngredients()


