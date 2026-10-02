"""Download only screenshot assets observed in the provided source guides."""
import concurrent.futures
import json
from pathlib import Path
from urllib.parse import urlsplit
from collect_program_sources import download

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'images/programs'


def save(url):
    filename = Path(urlsplit(url).path).name
    target = DIRECTORY / filename
    try:
        content, _ = download(url, target)
        if not (content.startswith(b'\xff\xd8\xff') or content.startswith(b'\x89PNG\r\n\x1a\n') or (content.startswith(b'RIFF') and content[8:12] == b'WEBP')):
            return url, {'error': 'The response is not a supported image.'}
        return url, {'path': '/images/programs/' + filename}
    except Exception as error:
        return url, {'error': str(error)}


if __name__ == '__main__':
    DIRECTORY.mkdir(exist_ok=True)
    guides = json.loads((ROOT / '.content-review/source-guides.json').read_text())
    urls = sorted({image['url'] for guide in guides for image in guide.get('screenshots', [])})
    assets = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for url, result in pool.map(save, urls):
            assets[url] = result
            if len(assets) % 100 == 0:
                print('Screenshots:', len(assets), 'of', len(urls), flush=True)
    (ROOT / 'data/screenshot-assets.json').write_text(json.dumps(assets, indent=2) + '\n')
    print('Saved', sum('path' in asset for asset in assets.values()), 'images;', sum('error' in asset for asset in assets.values()), 'failures.', flush=True)
