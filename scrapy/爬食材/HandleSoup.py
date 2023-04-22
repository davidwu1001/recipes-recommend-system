def handleSoup(soup,url):
    category = {"category":"","subcategories":[]}
    cate = soup.find("a",{'href':url}).text
    category['category'] = cate
    gridlist = soup.find_all("div",{'class':"gridlist"})
    for grid in gridlist:
        subcategory = {"subcategory":"","ingredients":[]}
        subcate = grid.find("h3").text
        subcategory['subcategory'] = subcate
        iList = grid.find_all("li")
        for item in iList:
            subcategory['ingredients'].append(item.find("a").text)
        category['subcategories'].append(subcategory)
    print(f"{cate}爬取完成")
    return category




