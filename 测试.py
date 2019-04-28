from raven.transport import requests
r = requests.get('https://www.baidu.com')
r.content
print(r.text)