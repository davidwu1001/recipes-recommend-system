def handleSoup(soup):
    if soup.find("img")['src'] == "//static.meishichina.com/v6/img/temp/404_1.png":
        # 网页不存在
        return False
    if not soup.find(id="recipe_title").text:
        #食谱不存在
        return False
    if not soup.find(id="recipe_De_imgBox"):
        #背景不存在
        return False
    def handleRecipe():
        recipe = {}
        # 食谱名称
        recipe['name'] = soup.find(id="recipe_title").text
        print("正在爬取：",recipe['name'])
        # 食谱工艺
        if soup.find("span", string="工艺"):
            recipe['process'] = soup.find("span", string="工艺").findParent("li").find("a").text

        # 食谱耗时
        if soup.find("span", string="耗时"):
            recipe['time_consuming'] = soup.find("span", string="耗时").findParent("li").find("a").text

        #食谱口味
        if soup.find("span", string="口味"):
            recipe['taste'] = soup.find("span", string="口味").findParent("li").find("a").text

        # 食谱难度
        if soup.find("span", string="难度"):
            recipe['difficulty'] = soup.find("span", string="难度").findParent("li").find("a").text

        # 食谱背景图片
        recipe['picture'] = soup.find(id="recipe_De_imgBox").find("img")['src']

        # 食谱说明
        if soup.find(id="block_txt1"):
            recipe['text'] = soup.find(id="block_txt1").text
        else:
            recipe['text'] = ""

        #食谱类别
        recipe['category'] = []
        cates = soup.find_all("a", {'class': "vest"})
        for cate in cates:
            recipe['category'].append(cate.text)
        return recipe

    def handleIngredients():
        ingredients = []

        fieldset = soup.find_all("fieldset", {"class": "particulars"})
        for index, item in enumerate(fieldset):
            type = item.find("legend").text
            for iitem in item.find_all("li"):
                ingredient = {}
                ingredient["name"] = iitem.find('b').text
                ingredient["amount"] = iitem.find("span", {"class": "category_s2"}).text
                ingredient["type"] = type
                ingredient["seq"] = index + 1
                ingredients.append(ingredient)
        return ingredients

    def handleProcedures():
        procedures = []

        recipeStep = soup.find("div", {"class": 'recipeStep'}).find_all("li")
        for index, item in enumerate(recipeStep):
            procedure = {}
            if item.find("img"):
                procedure['picture'] = item.find("img")['src']
            else:
                procedure['picture'] = ""

            procedure['text'] = item.find('div', {'class': "recipeStep_word"}).get_text('/')
            procedure['text'] = procedure['text'][
                                procedure['text'].find('/') + 1:]  # 为了去掉“1/准备好各种材料。配菜的尖椒、洋葱也可以用彩椒代替”。前面的数字
            procedure['seq'] = item.find('div', {'class': "recipeStep_num"}).text
            procedures.append(procedure)
        return procedures

    recipe = handleRecipe()
    procedure = handleProcedures()
    ingredient = handleIngredients()
    # print(f"{recipe['name']}爬取完成")
    return {"recipe":recipe,"procedure":procedure,"ingredient":ingredient}
