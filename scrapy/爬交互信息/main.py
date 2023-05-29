import json

from faker import Faker
fake = Faker()
from app import app
import urllib3
from Process_Recipe import process_recipe
from Process_User import process_user
from Parse_Url import parse_url
from utils.neo4j import graph
def setUserURLList():
    userUrlList = []
    for index in range(50):
        url1 = 'https://home.meishichina.com/pai/hot/page/'+str(index)+'/'
        url2 = 'https://home.meishichina.com/pai/new/page/' + str(index) + '/'
        url3 = 'https://home.meishichina.com/pai/elite/page/' + str(index) + '/'
        url4 = 'https://home.meishichina.com/pai/elite/page/' +str(index) + '/'
        urlList = [url1,url2,url3,url4]
        for url in urlList:
            soup = parse_url(url)
            if soup.find('div',{'class':'space_left'}):
                userList = soup.find('div',{'class':'space_left'}).find_all('li')
                for userSoup in userList:
                    userUrl = userSoup.find('a')['href']
                    userUrlList.append(userUrl)
                    print(f"新增{userUrl}")

    # 去重
    userUrlList = list(set(userUrlList))

    with open('./userUrlList.json','w') as f:
        print(f"共爬取{len(userUrlList)}个url")
        f.write(json.dumps(userUrlList))

def getUserURLList():
    with open('./userUrlList.json','r') as f:
        return json.load(f)
def store_txt():
    cypher = "match (n:Recipe)-[ne:need]->(i:Ingredient) with n as recipe,collect(i) as ingredients return recipe,ingredients"
    recipes = graph.run(cypher).data()
    # 计数
    num = 0
    with open("../爬取结果/recipes.txt",'r+',encoding="utf-8") as f:
        for recipe in recipes:
            num = num + 1
            ingredients = recipe['ingredients']
            ingredients_txt = ' '.join([ingredient['name'] for ingredient in ingredients])
            print(ingredients_txt)
            f.write(ingredients_txt+"\n")
    print(f"共{num}条记录")

if __name__ == "__main__":
    # 取消http警告
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # urlList =  getUserURLList()
    # with app.app_context():
    #     for url in urlList:
    #         process_user(url)
    store_txt()


