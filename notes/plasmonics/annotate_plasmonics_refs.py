# -*- coding: utf-8 -*-
import re
import json
import time
import math
import html
import difflib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import quote_plus, urlparse
import requests
import xml.etree.ElementTree as ET

INPUT = Path(r'C:\Users\27370\Desktop\project\optics_agent\notes\plasmonics\plasmonics_paper_refs_from_ppt.md')
OUTPUT = Path(r'C:\Users\27370\Desktop\project\optics_agent\notes\plasmonics\plasmonics_paper_refs_from_ppt_annotated.md')
UNRESOLVED = Path(r'C:\Users\27370\Desktop\project\optics_agent\notes\plasmonics\plasmonics_paper_refs_from_ppt_unresolved.json')

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) PaperMetaBot/1.0'})

cache = {}

def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'[\u3000\s]+', ' ', s)
    s = s.replace('“', '"').replace('”', '"').replace('’', "'")
    s = re.sub(r'[\[\]{}()《》<>「」『』,.;:!?|/\\]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def sim(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def strip_notes(s: str) -> str:
    # remove full-width / ascii parenthetical notes that are mostly commentary
    s = re.sub(r'（PPT[^）]*）', '', s)
    s = re.sub(r'\(PPT[^\)]*\)', '', s)
    s = re.sub(r'（[^）]{0,30}信息不完整[^）]*）', '', s)
    s = re.sub(r'\([^\)]{0,30}信息不完整[^\)]*\)', '', s)
    return s.strip()


def guess_title(text: str) -> str:
    s = strip_notes(text)
    # quoted title
    qs = re.findall(r'["“](.+?)["”]', s)
    if qs:
        # prefer longest quoted fragment
        qs = sorted(qs, key=len, reverse=True)
        q = qs[0].strip(' ,;。．')
        if len(q) > 4:
            return q
    # titles often hidden in PPT note after Chinese semicolon
    if '；' in s:
        parts = [p.strip() for p in s.split('；')]
        for p in reversed(parts):
            if re.search(r'[A-Za-z]', p) and len(p) > 6 and not p.lower().startswith('ppt'):
                return p.strip(' ,;。．')
    if ';' in s:
        parts = [p.strip() for p in s.split(';')]
        for p in reversed(parts):
            if re.search(r'[A-Za-z]', p) and len(p) > 6 and not p.lower().startswith('ppt'):
                return p.strip(' ,;。．')
    # title before first sentence boundary
    # if it starts with author/journal info, keep whole string
    if '. ' in s:
        first = s.split('. ', 1)[0].strip()
        if len(first) > 5 and re.search(r'[A-Za-z]', first):
            return first
    # if there is a comma and the first clause looks title-like
    if ',' in s:
        first = s.split(',', 1)[0].strip()
        if len(first) > 5 and re.search(r'[A-Za-z]', first):
            return first
    return s.strip(' ,;。．')


def extract_doi(s: str):
    m = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', s, re.I)
    return m.group(0) if m else None


def extract_arxiv_id(url_or_id: str):
    if not url_or_id:
        return None
    s = url_or_id.strip()
    s = s.replace('http://arxiv.org/abs/', '').replace('https://arxiv.org/abs/', '')
    s = s.replace('http://arxiv.org/pdf/', '').replace('https://arxiv.org/pdf/', '')
    s = s.replace('arXiv:', '')
    s = s.split('v')[0]
    s = s.strip('/')
    if re.match(r'\d{4}\.\d{4,5}', s) or re.match(r'[a-z\-]+/\d{7}', s, re.I):
        return f'arXiv:{s}'
    return None


def search_arxiv(query: str):
    if not query or len(query) < 8:
        return None
    cache_key = ('arxiv', norm(query))
    if cache_key in cache:
        return cache[cache_key]
    # try title search first, then all search
    for field in ('ti', 'all'):
        url = 'https://export.arxiv.org/api/query?search_query=' + quote_plus(f'{field}:"{query}"') + '&start=0&max_results=5'
        try:
            r = session.get(url, timeout=25)
            if r.status_code != 200:
                continue
            root = ET.fromstring(r.text)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            entries = []
            for entry in root.findall('atom:entry', ns):
                title = (entry.findtext('atom:title', default='', namespaces=ns) or '').strip().replace('\n', ' ')
                aid = entry.findtext('atom:id', default='', namespaces=ns) or ''
                entries.append((title, aid))
            if not entries:
                continue
            best = None
            best_score = 0.0
            for title, aid in entries:
                score = sim(query, title)
                if score > best_score:
                    best_score = score
                    best = (title, aid, score)
            if best and best[2] >= 0.78:
                arxiv = extract_arxiv_id(best[1])
                cache[cache_key] = (arxiv, best[2], best[0])
                return cache[cache_key]
        except Exception:
            pass
    cache[cache_key] = None
    return None


def search_crossref(query: str):
    if not query or len(query) < 4:
        return None
    cache_key = ('crossref', norm(query))
    if cache_key in cache:
        return cache[cache_key]
    url = 'https://api.crossref.org/works?query.bibliographic=' + quote_plus(query) + '&rows=5'
    try:
        r = session.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()['message']['items']
        if not data:
            cache[cache_key] = None
            return None
        best = None
        best_score = 0.0
        for item in data:
            title = ' '.join(item.get('title') or [])
            score = sim(query, title) if title else 0.0
            # small boost if year/page metadata overlaps
            if item.get('DOI'):
                score += 0.02
            if item.get('published-print') or item.get('published-online'):
                score += 0.01
            if score > best_score:
                best_score = score
                best = item
        if best:
            title = ' '.join(best.get('title') or [])
            doi = best.get('DOI')
            links = best.get('link') or []
            free = None
            for lk in links:
                ct = (lk.get('content-type') or '').lower()
                url = lk.get('URL') or lk.get('url')
                if url and 'pdf' in ct:
                    free = url
                    break
            cache[cache_key] = {
                'title': title,
                'doi': doi,
                'free_url': free,
                'score': best_score,
                'raw': best,
            }
            return cache[cache_key]
    except Exception:
        pass
    cache[cache_key] = None
    return None


def search_openalex(query: str):
    if not query or len(query) < 4:
        return None
    cache_key = ('openalex', norm(query))
    if cache_key in cache:
        return cache[cache_key]
    url = 'https://api.openalex.org/works?search=' + quote_plus(query) + '&per-page=5'
    try:
        r = session.get(url, timeout=30)
        r.raise_for_status()
        items = r.json().get('results') or []
        if not items:
            cache[cache_key] = None
            return None
        best = None
        best_score = 0.0
        for item in items:
            title = item.get('title') or ''
            score = sim(query, title)
            if item.get('doi'):
                score += 0.02
            if item.get('open_access', {}).get('is_oa'):
                score += 0.01
            if score > best_score:
                best_score = score
                best = item
        if best:
            oa = best.get('open_access') or {}
            bl = best.get('best_oa_location') or {}
            free_url = None
            for key in ('url_for_pdf', 'pdf_url', 'landing_page_url'):
                v = bl.get(key)
                if v and 'doi.org' not in v.lower():
                    free_url = v
                    break
            cache[cache_key] = {
                'title': best.get('title') or '',
                'doi': best.get('doi'),
                'arxiv': (best.get('ids') or {}).get('arxiv'),
                'free_url': free_url,
                'is_oa': oa.get('is_oa'),
                'score': best_score,
                'raw': best,
            }
            return cache[cache_key]
    except Exception:
        pass
    cache[cache_key] = None
    return None


def decide_meta(raw_line: str):
    cleaned = strip_notes(raw_line)
    title_guess = guess_title(cleaned)
    query = title_guess if title_guess and len(title_guess) >= 8 else cleaned

    arxiv = search_arxiv(title_guess if title_guess else query)
    if arxiv:
        arxiv_id, score, matched_title = arxiv
        if arxiv_id:
            return {
                'kind': 'arxiv',
                'value': arxiv_id,
                'query': query,
                'matched_title': matched_title,
                'confidence': round(score, 3),
            }

    # First try Crossref because it often provides DOI and direct OA links for older papers
    cr = search_crossref(query)
    oa = search_openalex(query)

    candidates = []
    if cr:
        candidates.append(('crossref', cr.get('score', 0.0), cr))
    if oa:
        candidates.append(('openalex', oa.get('score', 0.0), oa))
    candidates.sort(key=lambda x: x[1], reverse=True)
    best_source = candidates[0][0] if candidates else None
    best = candidates[0][2] if candidates else None

    # Prefer free full text URL if we have a reasonable match
    free_url = None
    if oa and oa.get('free_url'):
        free_url = oa['free_url']
    if cr and cr.get('free_url'):
        # Crossref PDF link wins if available
        free_url = cr['free_url'] or free_url

    if free_url:
        return {
            'kind': 'free_url',
            'value': free_url,
            'query': query,
            'matched_title': (best or {}).get('title') if isinstance(best, dict) else None,
            'confidence': round((best or {}).get('score', 0.0) if isinstance(best, dict) else 0.0, 3),
            'source': best_source,
        }

    doi = None
    matched_title = None
    confidence = 0.0
    if best_source == 'crossref' and cr:
        doi = cr.get('doi')
        matched_title = cr.get('title')
        confidence = cr.get('score', 0.0)
    elif best_source == 'openalex' and oa:
        doi = oa.get('doi')
        matched_title = oa.get('title')
        confidence = oa.get('score', 0.0)
    else:
        doi = (cr or {}).get('doi') or (oa or {}).get('doi')
        matched_title = (cr or {}).get('title') or (oa or {}).get('title')
        confidence = max((cr or {}).get('score', 0.0), (oa or {}).get('score', 0.0))

    if doi:
        doi = doi.replace('https://doi.org/', '').replace('http://doi.org/', '')
        return {
            'kind': 'doi',
            'value': doi,
            'query': query,
            'matched_title': matched_title,
            'confidence': round(confidence, 3),
            'source': best_source,
        }

    # Final fallback: try if OpenAlex located arXiv ID somehow
    if oa and oa.get('arxiv'):
        arxiv_id = extract_arxiv_id(oa.get('arxiv'))
        if arxiv_id:
            return {
                'kind': 'arxiv',
                'value': arxiv_id,
                'query': query,
                'matched_title': matched_title,
                'confidence': round(confidence, 3),
                'source': 'openalex',
            }

    return {
        'kind': 'unresolved',
        'value': None,
        'query': query,
        'matched_title': matched_title,
        'confidence': round(confidence, 3),
        'source': best_source,
    }


text = INPUT.read_text(encoding='utf-8')
lines = text.splitlines()
items = []
for idx, line in enumerate(lines):
    m = re.match(r'^(\d+)\.\s+(.*)$', line)
    if m:
        items.append((idx, int(m.group(1)), m.group(2)))

print(f'Found {len(items)} numbered items')

# Process unique queries first to improve speed
unique_queries = []
seen = set()
for _, _, raw in items:
    query = guess_title(strip_notes(raw))
    key = norm(query if query and len(query) >= 8 else strip_notes(raw))
    if key not in seen:
        seen.add(key)
        unique_queries.append((key, raw))

results_by_key = {}

max_workers = 10
with ThreadPoolExecutor(max_workers=max_workers) as ex:
    future_map = {}
    for key, raw in unique_queries:
        future = ex.submit(decide_meta, raw)
        future_map[future] = key
    done = 0
    total = len(future_map)
    for future in as_completed(future_map):
        key = future_map[future]
        try:
            results_by_key[key] = future.result()
        except Exception as e:
            results_by_key[key] = {'kind': 'unresolved', 'value': None, 'query': key, 'matched_title': None, 'confidence': 0.0, 'error': str(e)}
        done += 1
        if done % 10 == 0 or done == total:
            print(f'Progress: {done}/{total}')

new_lines = []
unresolved = []
for idx, line in enumerate(lines):
    new_lines.append(line)
    m = re.match(r'^(\d+)\.\s+(.*)$', line)
    if not m:
        continue
    raw = m.group(2)
    query = guess_title(strip_notes(raw))
    key = norm(query if query and len(query) >= 8 else strip_notes(raw))
    meta = results_by_key.get(key) or {'kind': 'unresolved', 'value': None, 'query': raw, 'matched_title': None, 'confidence': 0.0}
    if meta['kind'] == 'arxiv':
        new_lines.append(f'   - arXiv：{meta["value"]}')
    elif meta['kind'] == 'free_url':
        new_lines.append(f'   - 免费原文：{meta["value"]}')
    elif meta['kind'] == 'doi':
        new_lines.append(f'   - DOI：{meta["value"]}')
    else:
        note = '未能可靠检索（PPT 信息不完整或标题过于模糊）'
        new_lines.append(f'   - {note}')
        unresolved.append({'line': line, 'query': query or raw, 'matched_title': meta.get('matched_title'), 'confidence': meta.get('confidence', 0.0), 'source': meta.get('source')})

OUTPUT.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')
UNRESOLVED.write_text(json.dumps(unresolved, ensure_ascii=False, indent=2), encoding='utf-8')
print('Wrote', OUTPUT)
print('Unresolved:', len(unresolved))
