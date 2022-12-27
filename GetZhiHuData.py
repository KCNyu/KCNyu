from bs4 import BeautifulSoup
import requests
import re

readmePath = "README.md"

r = requests.get('https://www.zhihu.com/people/shengyuli')
soup = BeautifulSoup(r.content, "html.parser")
stars = soup.find_all(name='div', attrs={'class': 'css-zkfaav'})
agree, like, collection = 0, 0, 0
for star in stars:
    text = star.text
    if '赞同' in text:
        agree = re.findall('[0-9,]+', text)[0]
        break

likes = soup.find_all(name='div', attrs={'class': 'css-11cewt9'})
for like in likes:
    text = like.text
    if '喜欢' in text:
        like, collection = re.findall('[0-9,]+', text)
        break


follows = soup.find_all(name='strong', attrs={
                        'class': 'NumberBoard-itemValue'})
follow = follows[1].text

zhihu = '获得{}次赞同，{}次喜欢，{}次收藏，{}个关注'.format(
    agree, like, collection, follow)
print(zhihu)

with open(readmePath, "r") as readme:
    content = readme.read()

newContent = re.sub(r"(?<=<!\-\-START_SECTION:zhihu\-followers\-\->)[\s\S]*(?=<!\-\-END_SECTION:zhihu\-followers\-\->)",
                    f"\n{zhihu}\n", content)

with open(readmePath, "w") as readme:
    readme.write(newContent)
