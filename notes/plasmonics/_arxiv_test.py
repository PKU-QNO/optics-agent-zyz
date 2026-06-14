import requests
q='Plasmonics: Localization and guiding of electromagnetic energy in metal/dielectric structures'
url='https://export.arxiv.org/api/query?search_query=ti:%22'+requests.utils.quote(q)+'%22&start=0&max_results=3'
r=requests.get(url, timeout=30, headers={'User-Agent':'Mozilla/5.0'})
print(r.status_code)
print(r.text[:1000])
