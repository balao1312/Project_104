import requests, csv, urllib, pathlib, json
from bs4 import BeautifulSoup

headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}

#keyword_url_format = urllib.parse.quote(keyword)    # 中文字轉 url 格式


url = "https://m.104.com.tw/job/6xyu8"
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'lxml')
print(soup.prettify())