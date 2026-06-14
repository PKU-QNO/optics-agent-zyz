import urllib.request
print(urllib.request.urlopen('https://httpbin.org/get', timeout=20).read()[:80])
