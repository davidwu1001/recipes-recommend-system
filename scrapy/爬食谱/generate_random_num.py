import random
import json
nums = list(range(100000, 999999))
random_num = random.sample(nums,200000)
random_nums = []
for item in range(500):
    print(f"第{item + 1}批序号正在生成，还剩{500 - item - 1}批")
    start = item * 400
    end = start + 400
    random_nums.append(random_num[start:end])

with open('random_num.json','r+') as f:

        f.write(json.dumps(random_nums))

print("生成完成，结果存储到random_num.json文件中")

