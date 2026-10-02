"""Build state directories from the audited local source index, using the current site shell."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = json.loads((ROOT / 'data/source-inventory.json').read_text())
PROGRAMS = {p['slug']: p for p in INDEX['programs']}
CATEGORIES = {
    'food': ('Food assistance', 'Explore help with groceries, nutrition or meals.'),
    'housing': ('Housing assistance', 'Explore housing support and help with a housing crisis.'),
    'utilities': ('Utility assistance', 'Explore help with energy bills or home energy costs.'),
    'health': ('Health coverage', 'Explore public health coverage and health care assistance.'),
    'cash': ('Cash and income support', 'Explore public income support and family assistance.'),
    'childcare': ('Child care assistance', 'Explore help with child care costs.'),
    'other': ('Additional support', 'Explore assistance resources available in your state.'),
}


def category(title):
    for key, pattern in [('childcare', r'child.?care'), ('health', r'medicaid|medicare|chip|kidscare|kidcare|peachcare|health|ahcccs|medi-cal|kern medical|clinica'),
                         ('food', r'\bsnap\b|\bwic\b|nutrition|food|meal|calfresh|\bfns\b|3squares|basic food'),
                         ('utilities', r'liheap|energy|utility|utilities|weatherization|shutoff|power az'),
                         ('cash', r'tanf|cash|unemployment|\bssi\b|income|temporary assistance|temporary disability|tax|eitc|vita|homestead credit|grocery credit|kids credit|working family credit|calworks|general assistance|family investment|senior benefits|edd'),
                         ('housing', r'housing|rent|eviction|shelter|legal aid')]:
        if re.search(pattern, title, re.I):
            return key
    return 'other'


def shell(template, main, title, description, route):
    page = re.sub(r'<main\b.*?</main>', main, template, count=1, flags=re.S)
    page = re.sub(r'<script type="application/ld\+json">.*?</script>', '', page, flags=re.S)
    page = re.sub(r'<meta name="robots" content="noindex,follow">\s*', '', page)
    page = re.sub(r'<title>.*?</title>', '<title>' + html.escape(title) + '</title>', page)
    for prop in ['description', 'og:description', 'og:title', 'og:url']:
        value = title if prop == 'og:title' else 'https://www.publicbenefitfinder.org' + route if prop == 'og:url' else description
        page = re.sub(r'(<meta (?:name|property)="' + re.escape(prop) + r'" content=")[^"]*', lambda m: m[1] + html.escape(value, quote=True), page)
    page = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m[1] + 'https://www.publicbenefitfinder.org' + route, page)
    return page


def write_routes(routes):
    (ROOT / 'data/routes.json').write_text(json.dumps(routes, indent=2) + '\n')
    lines = ['DirectoryIndex index.html', 'Options -MultiViews', '', '<IfModule mod_rewrite.c>', 'RewriteEngine On', '']
    redirects_path = ROOT / 'data/redirects.json'
    redirects = json.loads(redirects_path.read_text()) if redirects_path.exists() else {}
    for old, target in redirects.items():
        lines.append(f'RewriteRule ^{re.escape(old.lstrip("/"))}$ {target} [R=301,L]')
    for route, filename in routes.items():
        lines += [r'RewriteCond %{THE_REQUEST} \s/+' + re.escape(filename) + r'(?:[?\s]) [NC]',
                  f'RewriteRule ^{re.escape(filename)}$ {route} [R=301,L]']
    lines += ['', 'RewriteCond %{REQUEST_FILENAME} -f [OR]', 'RewriteCond %{REQUEST_FILENAME} -d', 'RewriteRule ^ - [L]', '']
    for route, filename in routes.items():
        if route != '/':
            path = route.strip('/')
            lines += [f'RewriteRule ^{re.escape(path)}$ /{path}/ [R=301,L]', f'RewriteRule ^{re.escape(path)}/$ {filename} [L]']
    (ROOT / '.htaccess').write_text('\n'.join(lines + ['</IfModule>', '']))
    published = [route for route, filename in routes.items() if 'content="noindex,follow"' not in (ROOT / filename).read_text()]
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>https://www.publicbenefitfinder.org{route}</loc></url>\n' for route in published) + '</urlset>\n')


def build():
    details_path = ROOT / 'data/program-details.json'
    details = {p['slug']: p for p in json.loads(details_path.read_text())} if details_path.exists() else {}
    template = (ROOT / 'state-arizona.html').read_text()
    state_index = (ROOT / 'states.html').read_text()
    names = re.findall(r'<option(?: value="[^"]*")?>([^<]+)</option>', state_index)
    names = [n for n in names if n != 'Choose your state']
    source_states = {p['slug']: p for p in INDEX['help_pages']}
    states = []
    routes = json.loads((ROOT / 'data/routes.json').read_text())
    for name in names:
        slug = 'washington-dc' if name == 'District of Columbia' else name.lower().replace(' ', '-')
        assert slug in source_states, slug
        entries = []
        for program_slug in source_states[slug]['programs']:
            program = PROGRAMS[program_slug]
            if re.search(r'debt relief|credit repair|personal loan', program['title'], re.I):
                continue
            key = category(program['title'])
            tags = [tag for tag, pattern in [('children', r'\bwic\b|\bchip\b|kidscare|child|tanf|cash assistance'), ('senior', r'senior|medicare|older'), ('disabled', r'disabil|\bssi\b|medicaid'), ('veteran', r'veteran')] if re.search(pattern, program['title'], re.I)]
            detail = details.get(program_slug, {})
            guide = detail.get('route') or ('/programs/arizona-nutrition-assistance-snap/' if program_slug == 'arizona-nutrition-assistance-snap' else None)
            entries.append({'slug': program_slug, 'title': program['title'], 'category': key, 'tags': tags, 'description': detail.get('description', CATEGORIES[key][1]), 'guide': guide})
        state = {'slug': slug, 'name': name, 'programs': entries}
        states.append(state)
        route = f'/help/{slug}/'
        content = f'<main id="main"><section class="site-pagehead"><div class="pbf-wrap"><nav class="site-bc" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/help/">Browse by state</a></li><li aria-current="page">{html.escape(name)}</li></ol></nav><h1 class="site-h1">Assistance programs in {html.escape(name)}</h1><p class="site-lede">Explore public benefits and assistance resources by the kind of help you need. Agencies decide eligibility and availability.</p><a class="pbf-btn pbf-btn--primary" href="/find/">Find help</a></div></section><section class="site-body"><div class="pbf-wrap">'
        for key, (label, _) in CATEGORIES.items():
            group = [p for p in entries if p['category'] == key]
            if not group:
                continue
            content += f'<section class="site-state-section" id="{key}"><h2 class="pbf-h2">{label}</h2><ul class="pbf-results">'
            for program in group:
                title = html.escape(program['title'])
                heading = f'<a href="{program["guide"]}">{title}</a>' if program['guide'] else title
                action = f'<a class="pbf-link" href="{program["guide"]}">Read the application guide</a>' if program['guide'] else f'<a class="pbf-link" href="/help/{slug}/#{key}">Explore this type of assistance</a>'
                content += f'<li class="pbf-program" id="{program["slug"]}"><div class="pbf-program__main"><h3 class="pbf-h3 pbf-program__title">{heading}</h3><p>{program["description"]}</p></div><div class="pbf-program__actions">{action}</div></li>'
            content += '</ul></section>'
        content += '<p class="pbf-small pbf-muted">Program names come from our existing directory. Funding and rules can change; confirm details with the administering agency before applying.</p></div></section></main>'
        filename = f'state-{slug}.html'
        (ROOT / filename).write_text(shell(template, content, f'Assistance programs in {name} | Public Benefit Finder', f'Explore public benefit programs and assistance resources in {name}.', route))
        routes[route] = filename
    (ROOT / 'data/finder-programs.json').write_text(json.dumps({'states': states}, indent=2) + '\n')
    # State links and select values must each point to their own state.
    for state in states:
        name, slug = state['name'], state['slug']
        state_index = state_index.replace(f'<a href="/help/arizona/">{name}</a>', f'<a href="/help/{slug}/">{name}</a>')
        state_index = state_index.replace(f'<option>{name}</option>', f'<option value="{slug}">{name}</option>')
    state_index = state_index.replace('action="/help/arizona/"', 'action="/help/" data-state-picker')
    (ROOT / 'states.html').write_text(state_index)
    routes['/programs/arizona-nutrition-assistance-snap/'] = 'guide-arizona-snap.html'
    fragment = ROOT / 'data/arizona-snap-content.html'
    if fragment.exists():
        page = shell((ROOT / 'guide-snap.html').read_text(), fragment.read_text(),
                     'Arizona Nutrition Assistance (SNAP): how to apply | Public Benefit Finder',
                     'Learn how to apply for Arizona SNAP, prepare documents, complete the interview and track your case. Includes application screenshots and FAQs.',
                     '/programs/arizona-nutrition-assistance-snap/')
        (ROOT / 'guide-arizona-snap.html').write_text(page)
    write_routes(routes)
    print(f'Built {len(states)} state directories and finder catalog.')


if __name__ == '__main__':
    build()
