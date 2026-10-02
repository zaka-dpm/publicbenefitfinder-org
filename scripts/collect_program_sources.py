"""Collect public source facts and check agency links. Cached HTML stays outside the repo."""
import concurrent.futures
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path('/tmp/pbf-program-source-cache')
CACHE.mkdir(exist_ok=True)
USER_AGENT = 'Mozilla/5.0 (compatible; PublicBenefitFinderContentReview/1.0)'
VOID = {'img', 'meta', 'input', 'br', 'hr', 'link', 'source', 'wbr', 'area', 'base', 'embed', 'param', 'track', 'col'}


class Node:
    def __init__(self, tag='', attrs=None):
        self.tag, self.attrs, self.children = tag, dict(attrs or []), []

    def text(self):
        if self.tag in {'script', 'style', 'svg'}:
            return ''
        return re.sub(r'\s+', ' ', ' '.join(c.text() if isinstance(c, Node) else c for c in self.children)).strip()

    def all(self, tag):
        found = []
        for child in self.children:
            if isinstance(child, Node):
                if child.tag == tag:
                    found.append(child)
                found.extend(child.all(tag))
        return found


class Tree(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Node('root')
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def download(url, filename=None):
    if filename and filename.exists():
        return filename.read_bytes(), url
    last = None
    for attempt in range(2):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            with urllib.request.urlopen(request, timeout=18) as response:
                content, final = response.read(3000000), response.url
                if filename:
                    filename.write_bytes(content)
                return content, final
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last = error
            if isinstance(error, urllib.error.HTTPError) and error.code in {400, 401, 403, 404, 410}:
                break
            if attempt == 0:
                time.sleep(1)
    raise last


def collect(program):
    slug = program['slug']
    url = 'https://usaassistance.org/programs/' + slug + '/'
    try:
        raw, _ = download(url, CACHE / (slug + '.html'))
        document = Tree(raw.decode('utf-8', errors='replace')).root
        article = document.all('article')[0]
        result = {'slug': slug, 'title': program['title'], 'source_url': url,
                  'source_updated': '', 'eligibility': [], 'steps': [], 'documents': [],
                  'faqs': [], 'screenshots': [], 'agency_url': '', 'phones': [], 'agency_check': {}}
        for p in article.all('p'):
            date = re.search(r'Last updated\s+(.+)', p.text())
            if date:
                result['source_updated'] = date[1]
                break
        for section in article.all('section'):
            headings = section.all('h2') + section.all('h3')
            heading = headings[0].text().lower() if headings else ''
            if heading == 'who qualifies':
                result['eligibility'] = [li.text() for li in section.all('li')]
            elif heading == 'how to apply':
                result['steps'] = [p.text() for p in section.all('p') if p.text()]
            elif heading == 'common questions':
                for detail in section.all('details'):
                    summary, paragraphs = detail.all('summary'), detail.all('p')
                    if summary and paragraphs:
                        result['faqs'].append({'question': summary[0].text(), 'answer': ' '.join(p.text() for p in paragraphs)})
        for heading in article.all('h3'):
            if heading.text().lower() == 'what to have ready':
                # Its parent section includes the application steps as well; keep only the checklist UL.
                for section in article.all('section'):
                    if heading in section.all('h3'):
                        lists = section.all('ul')
                        if lists:
                            result['documents'] = [li.text() for li in lists[-1].all('li')]
        for link in article.all('a'):
            if link.text().startswith('Official site'):
                result['agency_url'] = link.attrs.get('href', '')
                break
        result['phones'] = list(dict.fromkeys(re.findall(r'\b(?:1[- ])?\(?\d{3}\)?[- ]\d{3}[- ]\d{4}\b', article.text())))
        for figure in article.all('figure'):
            images, captions = figure.all('img'), figure.all('figcaption')
            if images:
                image = images[0]
                src = image.attrs.get('src', '')
                if urllib.parse.urlsplit(src).hostname == 'cdn.sanity.io':
                    result['screenshots'].append({'url': src.split('?')[0], 'alt': image.attrs.get('alt', ''), 'caption': captions[0].text() if captions else ''})
        result['financial_review_needed'] = any(re.search(r'\$|percent|income limit|poverty', text, re.I) for text in result['eligibility'] + result['steps'] + [faq['answer'] for faq in result['faqs']])
        return result
    except Exception as error:
        return {'slug': slug, 'title': program['title'], 'source_url': url, 'error': str(error)}


def check_agency(url):
    digest = hashlib.sha256(url.encode()).hexdigest()
    try:
        content, final = download(url, CACHE / ('agency-' + digest + '.html'))
        text = Tree(content.decode('utf-8', errors='replace')).root.text()
        blocked = bool(re.search(r'just a moment|verify you are human|access denied|request blocked', text[:2000], re.I))
        return {'status': 'blocked' if blocked else 'reachable', 'url': final, 'text_characters': len(text), 'checked': '2026-10-01', 'facts_verified': False}
    except Exception as error:
        return {'status': 'unavailable', 'error': str(error), 'checked': '2026-10-01', 'facts_verified': False}


def main():
    programs = json.loads((ROOT / 'data/source-inventory.json').read_text())['programs']
    output = ROOT / '.content-review/source-guides.json'
    output.parent.mkdir(exist_ok=True)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(collect, programs):
            results.append(result)
            if len(results) % 25 == 0:
                print('Collected', len(results), 'of', len(programs), flush=True)
                output.write_text(json.dumps(results, indent=2) + '\n')
    output.write_text(json.dumps(results, indent=2) + '\n')
    urls = sorted({p.get('agency_url', '') for p in results if p.get('agency_url', '').startswith('https://')})
    checks = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for url, result in zip(urls, pool.map(check_agency, urls)):
            checks[url] = result
            if len(checks) % 25 == 0:
                print('Checked agency links:', len(checks), 'of', len(urls), flush=True)
    for result in results:
        if result.get('agency_url'):
            result['agency_check'] = checks.get(result['agency_url'], {'status': 'not_checked', 'facts_verified': False})
    output.write_text(json.dumps(results, indent=2) + '\n')
    print('Saved', len(results), 'source records;', sum('error' in p for p in results), 'source failures;', len(checks), 'agency URL checks.', flush=True)


if __name__ == '__main__':
    main()
