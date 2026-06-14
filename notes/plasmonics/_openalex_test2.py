import requests, json
q='Plasmonics: Localization and guiding of electromagnetic energy in metal/dielectric'
url='https://api.openalex.org/works?search='+requests.utils.quote(q)+'&per-page=3'
r=requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=20)
print(r.status_code)
obj=r.json()
for item in obj['results']:
    print('TITLE:',item.get('title'))
    print('ARXIV:',item.get('ids',{}).get('arxiv'))
    print('DOI:',item.get('doi'))
    print('OA:',item.get('open_access',{}).get('is_oa'))
    bl=item.get('best_oa_location') or {}
    print('BURL:', bl.get('url_for_pdf') or bl.get('landing_page_url') or bl.get('pdf_url'))
    print('---')
