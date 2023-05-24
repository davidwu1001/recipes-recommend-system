from faker import Faker
fake = Faker()
import requests
from bs4 import BeautifulSoup
def parse_url(url):
    """
    解析url
    :param url:
    :return: 解析后的soup对象
    """
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
        return soup
    except requests.exceptions.ProxyError as e:
        print("代理错误：", e)
    except requests.exceptions.RequestException as e:
        print("请求错误：", e)