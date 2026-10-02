"""Create local editorial drafts. Source collection is not an eligibility verification."""
import html
import json
import re
from pathlib import Path
from build_directory import ROOT, CATEGORIES, category, shell, write_routes

E = html.escape
EXCLUDED = {'credit-org-free-nonprofit-credit-counseling', 'nfcc-nonprofit-credit-counseling'}
PROFILES = [
 (r'\bwic\b', 'Nutrition support for pregnancy, infants and young children.', 'WIC provides approved foods and nutrition services. The clinic assesses eligibility and nutritional needs.', 'Contact the WIC clinic to arrange an assessment. Ask who should attend and which records to bring.'),
 (r'\bsnap\b|calfresh|food stamps|3squares|food assistance|basic food', 'Help with grocery costs through a food assistance program.', 'Approved households receive food benefits. The agency calculates the amount from household circumstances and current program rules.', 'Start with the program application instructions. Ask about an eligibility interview and faster processing if food and money are running out.'),
 (r'211|2-1-1', 'A referral service for finding assistance in your community.', 'This service helps you locate providers. A referral does not guarantee funding or approval from the provider.', 'Describe your location and the help you need. Ask for provider contact details, intake hours and any application requirements.'),
 (r'weatherization', 'Home improvements to reduce energy use and costs.', 'An approved provider evaluates the home and identifies eligible improvements. This is different from a monthly utility bill payment.', 'Find the local weatherization provider and ask about intake, the home assessment and permission needed if you rent.'),
 (r'liheap|energy|utility|utilities|heating|pipp|care.fera', 'Assistance with energy bills or household utility costs.', 'Support may involve bill payments, discounts or emergency assistance. Funding, seasons and utility participation can affect availability.', 'Check the provider’s intake instructions. Explain any shutoff deadline and ask your utility about payment arrangements while the application is reviewed.'),
 (r'medicaid|chip|kidscare|medi-cal|ahcccs|health|medicare', 'Help finding health coverage or accessing health services.', 'The program’s coverage and eligibility depend on its rules and the applicant’s circumstances. Check which services and providers are included.', 'Use the coverage application instructions. Identify everyone seeking coverage and ask about the eligibility pathway that applies to each person.'),
 (r'unemployment', 'Income support after a qualifying loss of work.', 'The unemployment agency reviews work history, earnings and the circumstances of separation. Continuing claims may have separate reporting requirements.', 'Follow the state claim instructions. Gather employer details and dates of work, and read the directions for weekly certifications.'),
 (r'tax|eitc|vita', 'Tax credits or help preparing an eligible tax return.', 'Credits depend on the tax year and your circumstances. A tax preparation service can help identify which credits apply.', 'Check the relevant tax year and filing instructions. Collect income statements and dependent information before filing.'),
 (r'legal|eviction', 'Legal information or assistance with a housing or civil issue.', 'Providers assess the legal issue, service area and intake criteria. Representation depends on their capacity and the type of case.', 'Contact the provider promptly. Give the date of any hearing or response deadline and keep court papers and notices together.'),
 (r'child.?care', 'Help with eligible child care expenses.', 'Assistance can depend on household circumstances, the reason care is needed and the provider’s participation.', 'Ask about the application, provider approval and any waiting list before arranging care.'),
 (r'tanf|cash|temporary|\bssi\b', 'Cash or income assistance for eligible households.', 'The administering agency evaluates household circumstances and program requirements before setting payments.', 'Check the application instructions and any interview, employment or reporting requirements that apply to your case.'),
]

def profile(title):
 for pattern, *values in PROFILES:
  if re.search(pattern, title, re.I): return values
 return ['Assistance resources and services for eligible applicants.', 'The provider explains the services available, its service area and any intake requirements.', 'Contact the listed provider to ask about current intake and the next steps for your situation.']

def factors(guide):
 text = ' '.join(guide['eligibility']).lower()
 out = []
 for pattern, description in [
  (r'income|poverty|low-income', 'Household income and the program’s current income guidelines'),
  (r'residen|live in|living in', 'Residence within the program’s service area'),
  (r'pregnan|postpartum|breastfeed', 'Pregnancy or the period after childbirth'),
  (r'child|infant|dependent', 'Children or dependents in the household'),
  (r'disab', 'Disability-related eligibility pathways'),
  (r'older|elder|senior|65|60', 'Age-related eligibility pathways'),
  (r'nutrition', 'A nutrition assessment'),
  (r'work|employ|earnings', 'Employment or earnings history'),
  (r'asset|resource', 'Countable resources'),
  (r'veteran|military', 'Military or veteran status')]:
  if re.search(pattern,text): out.append(description)
 return out

def build():
 guides=json.loads((ROOT/'.content-review/source-guides.json').read_text())
 overrides=json.loads((ROOT/'data/agency-link-overrides.json').read_text())
 assets=json.loads((ROOT/'data/screenshot-assets.json').read_text())
 routes=json.loads((ROOT/'data/routes.json').read_text())
 template=(ROOT/'guide-snap.html').read_text()
 catalog=[]
 for g in guides:
  if g['slug'] in overrides:
   g['agency_url']=overrides[g['slug']]['url']
  if g['slug'] in EXCLUDED or re.search(r'credit counseling|debt relief|credit repair',g['title'],re.I): continue
  slug,title=g['slug'],g['title']
  route='/programs/'+slug+'/'
  if slug=='snap-food-stamps':
   route='/programs/snap/'
   routes.pop('/programs/snap-food-stamps/',None)
  description,benefits,application=profile(title)
  content_path=ROOT/'data/guide-content'/f'{slug}.json'
  authored=json.loads(content_path.read_text()) if content_path.exists() else {}
  description=authored.get('description',description)
  record={'slug':slug,'title':title,'route':route,'description':description,'category':category(title),'editorial_status':'draft','agency_url':g['agency_url'],'source_url':g['source_url'],'agency_check':g['agency_check']['status'],'screenshots':len(g['screenshots'])}
  record['editorial_status']=authored.get('status','draft')
  if slug=='arizona-nutrition-assistance-snap':
   record['editorial_status']='reviewed'; catalog.append(record); continue
  items=factors(g)
  eligibility='<p>The source guide identifies these factors. They are a starting point, not a complete eligibility test:</p><ul>'+''.join('<li>'+E(x)+'</li>' for x in items)+'</ul>' if items else '<p>Ask the provider about its service area and intake criteria. A referral service may be open broadly even when the programs it refers to have separate eligibility rules.</p>'
  docs=[]
  text=' '.join(g['documents']).lower()
  for pattern,label in [(r'\bid\b|identity','Identity records for applicants'),(r'income|pay|wage','Recent income records'),(r'residen|address','Evidence of your address'),(r'social security','Social Security information for applicants, if requested'),(r'utility|bill','Utility account and bill information'),(r'rent|lease','Lease, rent or housing records'),(r'benefit|enrollment|medicaid|snap','Records of existing benefit enrollment'),(r'child|birth','Documents concerning children in the application')]:
   if re.search(pattern,text): docs.append(label)
  documents='<p>Examples mentioned in the source checklist:</p><ul>'+''.join('<li>'+E(x)+'</li>' for x in docs)+'</ul><p>Confirm the exact list with the provider. Ask how to proceed if a requested document is difficult to obtain.</p>' if docs else '<p>Ask the provider for its document checklist before submitting personal records. Requirements depend on the service and your circumstances.</p>'
  agency=E(g['agency_url'],quote=True)
  faq=[('Where do I start?',application),('Does this guide determine whether I qualify?','No. The provider reviews your circumstances and makes the decision. Use its current instructions and decision notices.'),('Are the amounts shown in screenshots current?','The screenshots are historical references from August 2026. Check current agency rules before relying on a dollar amount, threshold or deadline.')]
  faq=authored.get('faqs',faq)
  if not authored and re.search(r'211|2-1-1',title): faq[1]=('Does a referral mean my bill will be paid?','No. Contact the referred provider to find out whether funding is available and whether your household qualifies.')
  photos=''
  seen_images=set()
  for image in g['screenshots']:
   if image['url'] in seen_images: continue
   seen_images.add(image['url'])
   asset=assets.get(image['url'],{})
   if 'path' not in asset: continue
   path=E(asset['path'],quote=True)
   photos+=f'<figure class="site-screenshot"><a href="{path}"><img src="{path}" width="1200" height="844" loading="lazy" alt="{E(image["alt"],quote=True)}"></a><figcaption>August 2026 reference screenshot.</figcaption></figure>'
  parts={'who':('Who can apply',eligibility),'get':('What help is available','<p>'+E(benefits)+'</p>'),'docs':('Documents to prepare',documents),'apply':('How to get started','<p>'+E(application)+f'</p><p><a class="pbf-btn pbf-btn--primary" href="{agency}">Visit the program website</a></p><p>Keep your confirmation or referral details. Follow any document requests and deadlines in the provider’s notices.</p>'),'screenshots':('Website screenshots','<p>These images show the pages captured in August 2026. Website screens and rules may have changed.</p>'+photos if photos else '<p>No reference screenshot is available for this program yet.</p>'),'questions':('Common questions','<div class="site-qa">'+''.join(f'<details class="site-qa__item"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q,a in faq)+'</div>'),'sources':('Sources and review',f'<p><a href="{agency}">Program website</a> · <a href="{E(g["source_url"],quote=True)}">Source guide and screenshot reference</a></p><p class="pbf-small">Local editorial draft. Current eligibility, application details and financial figures still require agency review.</p>')}
  for key,body in authored.get('sections',{}).items():
   label=parts[key][0] if key in parts else 'After applying'
   parts[key]=(label,body)
  if slug=='snap-food-stamps':
   states=json.loads((ROOT/'data/finder-programs.json').read_text())['states']
   links=[]
   for state in states:
    snap=next((p for p in state['programs'] if re.search(r'\bsnap\b|calfresh|3squares|basic food|food assistance',p['title'],re.I)),None)
    link='/programs/'+snap['slug']+'/' if snap else '/help/'+state['slug']+'/#food'
    links.append(f'<li><a href="{link}">{E(state["name"])}</a></li>')
   parts['apply']=('How to apply',parts['apply'][1]+'<h3 class="pbf-h3">Find your state’s SNAP guide</h3><ul class="site-state-links">'+''.join(links)+'</ul>')
  if authored:
   parts['sources']=('Sources and review',parts['sources'][1]+f'<p class="pbf-small">Historical screenshots: <a href="{E(g["source_url"],quote=True)}">source reference</a>.</p>')
  parts={key:parts[key] for key in ['who','get','docs','apply','after','screenshots','questions','sources'] if key in parts}
  toc=''.join(f'<li><a href="#{key}">{label}</a></li>' for key,(label,body) in parts.items())
  article=''.join(f'<section id="{key}"><h2 class="pbf-h2">{label}</h2>{body}</section>' for key,(label,body) in parts.items())
  introduction=authored.get('introduction',description)
  main=f'<main id="main"><section class="site-pagehead site-pagehead--guide"><div class="pbf-wrap"><nav class="site-bc" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/programs/">Program guides</a></li><li aria-current="page">{E(title)}</li></ol></nav><span class="pbf-badge pbf-badge--neutral">Local content draft</span><h1 class="site-h1">{E(title)}</h1><p class="site-lede">{E(introduction)}</p></div></section><div class="pbf-wrap site-guide"><aside class="site-toc" aria-label="On this page"><h2 class="site-toc__title">On this page</h2><ol>{toc}</ol></aside><article class="site-article">{article}</article></div></main>'
  page=shell(template,main,title+' | Public Benefit Finder',description,route)
  if record['editorial_status']=='reviewed':
   page=page.replace('Local content draft','Reviewed October 1, 2026')
  page=re.sub(r'<script type="application/ld\+json">.*?</script>','',page,flags=re.S)
  if record['editorial_status']=='reviewed':
   schema={'@context':'https://schema.org','@type':'FAQPage','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in faq]}
   page=page.replace('</head>','<script type="application/ld+json">'+json.dumps(schema).replace('<','\\u003c')+'</script>\n</head>')
  # Drafts must not be accidentally indexed while editorial review is pending.
  if record['editorial_status']!='reviewed':
   page=page.replace('</head>','<meta name="robots" content="noindex,follow">\n</head>')
  filename='guide-snap.html' if slug=='snap-food-stamps' else 'guide-'+slug+'.html'
  (ROOT/filename).write_text(page)
  routes[route]=filename
  catalog.append(record)
 (ROOT/'data/program-details.json').write_text(json.dumps(catalog,indent=2)+'\n')
 index='<main id="main"><section class="site-pagehead"><div class="pbf-wrap"><h1 class="site-h1">Program guides</h1><p class="site-lede">Browse public benefits and community assistance resources.</p><p class="pbf-small">Local preview: most expanded guides are editorial drafts pending verification. Reviewed guides are marked on their pages.</p><form class="site-search" action="/programs/" role="search" data-guide-search><label class="pbf-label" for="q">Search by program or state</label><div class="site-where__row"><input class="pbf-input" id="q" name="q" type="search" autocomplete="off"><button class="pbf-btn pbf-btn--primary" type="submit">Search</button></div></form></div></section><section class="site-body"><div class="pbf-wrap"><div class="site-groups">'
 for key,(label,_) in CATEGORIES.items():
  group=[p for p in catalog if p['category']==key]
  if not group: continue
  index+=f'<section class="site-group"><h2 class="pbf-h2">{label}</h2><ul>'+''.join(f'<li><a href="{p["route"]}">{E(p["title"])}</a></li>' for p in sorted(group,key=lambda p:p['title']))+'</ul></section>'
 index+='</div></div></section></main>'
 (ROOT/'programs.html').write_text(shell((ROOT/'programs.html').read_text(),index,'Program guides | Public Benefit Finder','Browse public benefit and community assistance guides by program or state.','/programs/'))
 write_routes(routes)
 print('Built',len(catalog),'guides;',sum(p['editorial_status']!='reviewed' for p in catalog),'require editorial review.')

if __name__=='__main__': build()
