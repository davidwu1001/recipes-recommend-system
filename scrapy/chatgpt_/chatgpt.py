import sys
import openai
from openai.error import OpenAIError
from scrapy.chatgpt_.config import OPENAI_API_KEY
import time
openai.api_key = OPENAI_API_KEY
def getRecipeSeasonAndArea(q):
    messages = [{"role": "system", "content": "You are a helpful assistant."}, {'role': "user",'content': '帮我在互联网上查询整理一下，青苹果这个食材的时令和地区，学习一下这个格式，{"spring":["湖南","江苏","浙江","福建"],"summer":["江苏","浙江"],"autumn":["黑龙江","吉林","辽宁","山东"],"winter":[]}，把上面的时令和地区用这个格式再回答一遍，之后我会给你食材名称，你仍然以这个格式回答我，记住一定要是这个格式'}]  # 存储对话
    messages.append({"role": "user", "content": q})
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages= messages,
            timeout= 5,
            stream = True,
            temperature=0.2

        )
        content = ''
        for chunk in resp:
            res = chunk['choices'][0]['delta']
            if "content" in res:
                content += res['content']

        messages.append({"role": "assistant", "content": content})

        try:
            start = content.index('{')  # 截取{
            end = content.index('}')  # 截取}
        except ValueError:  # 避免chatgpt也找不到这个食材的时令信息 比如马蹄粉
            return {"spring":[],"summer":[],"autumn":[],"winter":[]}
        content = eval(content[start:end+1])

        # 缺省处理
        # 避免gpt只吐出来一个时令
        if "spring" not in content:
            content['spring'] = []
        if "summer" not in content:
            content['summer'] = []
        if "autumn" not in content:
            content['autumn'] = []
        if "winter" not in content:
            content['winter'] = []

        return content
    except OpenAIError as e:
        print("Warning! OpenAI API错误\n",e)
        print("tips:兄弟检查梯子啦")
        return False

def main():
    q = ['橙子']
    for item in q:
        answer = getRecipeSeasonAndArea(item)

        print(answer)
        print(type(answer))
if __name__ == "__main__":
    main()


