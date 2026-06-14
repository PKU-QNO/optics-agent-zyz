import requests
url='https://api.openalex.org/works?search=Plasmonics%3A%20Localization%20and%20guiding%20of%20electromagnetic%20energy%20in%20metal%2Fdielectric&per-page=1'
resp=requests.get(url, timeout=20, headers={'User-Agent':'Mozilla/5.0'})
print(resp.status_code)
print(resp.text[:500])
