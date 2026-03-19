import requests

res = requests.get("https://ie.zafu.edu.cn/info/1112/5445.htm")
res.encoding = 'utf-8'
with open("./res.html", "w", encoding="utf-8") as f:
      f.write(res.text)