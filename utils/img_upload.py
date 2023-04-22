import os
from uuid import uuid4
from flask import current_app  # current_app 属于应用上下文，代表项目中的app本身

def img_upload(img):
    if not img:
        return None

    # 将图片名按照 .  进行切分， 找到最后一个元素，也就是  文件的后缀名
    end_name = img.filename.rsplit('.')[-1]

    # 通过文件的后缀名判断 身份为 合法的  图片
    if end_name not in ['jpg', 'png', 'gif', 'jpeg']:
        return None

    # 将 图片对象 存入 本地，然后将 路径 存入 数据库
    MEDIA = current_app.config['UPLOAD_FOLDER']  # 从app的配置项，取出 MEDIA的路径
    filename = str(uuid4()) + '.' + end_name  # 为了生成一个不重复的 文件名
    img_path = os.path.join(MEDIA, filename)  # 将路径和文件名拼接在一起，方便保存文件

    img.save(img_path)  # 将图片对象保存到 本地

    return {"filename":filename,"img_path":img_path}