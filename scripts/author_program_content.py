"""Build source-adapted editorial copy, retaining a separate factual review status.

Amounts, percentages, deadlines and legal exclusions are never inferred from an old
source. Existing agency-reviewed articles are preserved.
"""
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from collect_program_sources import Tree, CACHE
from guide_profiles import choose

ROOT=Path(__file__).resolve().parents[1]
E=html.escape


def paragraphs(*items):
 return ''.join('<p>'+E(x)+'</p>' for x in items if x)


def primary_text(url):
 path=CACHE/('agency-'+hashlib.sha256(url.encode()).hexdigest()+'.html')
 if not path.exists():return ''
 raw=path.read_bytes()
 if raw.startswith(b'%PDF'):return ''
 text=Tree(raw.decode(errors='replace')).root.text()
 if re.search(r'please solve this captcha|performing security verification|requested url was rejected|not available.*outside|access denied',text,re.I):return ''
 if len(text)<500:return ''
 return text


def document_labels(g,kind):
 text=' '.join(g['documents']).lower()
 # Some source pages omit the dedicated checklist but name records in the steps.
 if not text:text=' '.join(g['steps']).lower()
 patterns=[
  (r'photo id|\bid\b|identity|identification','Identification for the applicants or account holder'),
  (r'income|pay.?stub|wages|earnings','Income records for the relevant household members'),
  (r'proof.*(?:address|residen)|proof of where you live','Evidence of your address or residence'),
  (r'social security','Social Security information for people applying, as requested'),
  (r'immigration|citizenship','Citizenship or immigration records where required'),
  (r'resources|assets','Information about resources the program counts'),
  (r'utility|electric|gas bill|fuel bill','Current utility or fuel bills and account details'),
  (r'shut.?off|disconnect|eviction|notice to quit','Any shutoff, eviction or other emergency notice'),
  (r'lease|tenancy|rent certificate|property tax|mortgage','Relevant tenancy, rent, mortgage or property tax records'),
  (r'child.*(?:information|lives|details)|birth certificate','Records concerning the child or dependent applying'),
  (r'child.?care|day.?care','Child care or provider information relevant to the application'),
  (r'work.*(?:schedule|activity)|school.*(?:schedule|activity)|job.search','Work, job-search or school activity records'),
  (r'enrollment|enrolment|proof of.*(?:snap|medicaid|benefits)','Evidence of enrollment in another qualifying benefit'),
  (r'employer|work history|employment history','Employer details and work history'),
  (r'discharge|dd.?214|service records','Military service or discharge records'),
  (r'court papers|court documents|lender letters','Court papers or correspondence concerning the issue'),
  (r'w-?2|1099','Tax-year income statements, such as W-2 or 1099 records')]
 labels=[label for pattern,label in patterns if re.search(pattern,text)]
 if kind=='referral':
  return paragraphs('For an initial referral, prepare your location, the kind of help needed and any deadline. Ask the referred provider for its own document requirements; a referral conversation is different from a benefit application.')
 if kind in {'crisis','property','employment','foodbank','navigation'} and not labels:
  return paragraphs('Check the provider’s intake instructions before sending personal records. Explain your location and the service needed, then ask which documents are necessary for that specific request.')
 if not labels:
  return paragraphs('The source does not give a complete document checklist for this program. Use the program website or contact the provider to get the list for your request before submitting records.')
 return '<p>Prepare the records relevant to your situation:</p><ul>'+''.join('<li>'+E(x)+'</li>' for x in labels)+'</ul>'+paragraphs('This is a preparation list, not a requirement to send every record in advance. The provider confirms the evidence needed and how to submit it securely.')


def source_conditions(g,kind):
 text=' '.join(g['eligibility']).lower()
 conditions=[]
 if kind=='referral':return ['The referral service is available to people seeking resources in its service area. Providers reached through it have their own eligibility rules.']
 if kind=='crisis':return ['People seeking emotional or crisis support can contact 988. This is not an income-tested benefits application.']
 if kind=='wic':
  conditions=['WIC has eligibility categories for pregnancy, the period after childbirth, breastfeeding, infants and young children. The clinic checks the category that applies to the applicant.', 'The clinic assesses nutritional needs and the applicable income and residence requirements.']
 elif kind=='unemployment':
  conditions=['The agency checks qualifying work and earnings, the circumstances of the job separation and the requirements for continuing claims.']
 elif kind=='weatherization':
  conditions=['The local provider checks household eligibility and whether the home can receive approved weatherization work. An assessment determines the measures offered.']
 elif kind=='tax':
  conditions=['Use the eligibility rules for the tax year being claimed. Residency, income and any qualifying-child or housing conditions must be checked together.']
 elif kind=='snap':
  conditions=['The office assesses income, household circumstances and the program’s other eligibility rules. Having wages does not automatically prevent a household from applying.']
 elif kind=='health':
  conditions=['Ask which eligibility pathway fits each applicant. Children, adults, pregnant applicants and people with a disability may be assessed under different rules.']
 elif kind=='childcare':
  conditions=['The office checks household eligibility and the activity for which care is needed. The child and provider must also meet the program’s rules.']
 elif kind=='legal':
  conditions=['The provider checks the location, type of legal problem and its intake rules. Eligibility for free information can differ from eligibility for representation.']
 elif kind=='energy':
  conditions=['The provider checks the household, energy account or fuel need and the eligibility rules for the service requested. Emergency intake can have separate conditions.']
 elif kind=='cash':
  conditions=['The office assesses the household members applying, income and any other program conditions. The eligibility pathway depends on the type of cash assistance.']
 else:
  conditions=['Check the provider’s service area and intake rules for the help you need. Availability of one service does not establish eligibility for every program it offers.']
 # Preserve distinct facts as questions to resolve when the primary evidence does not
 # establish a current rule. This avoids publishing historical criteria as current law.
 if kind=='cash' and re.search(r'dependent child|families with.*child|responsible for a child',text):
  conditions.append('For this family assistance program, prepare the dependent child’s details and ask how age, schooling and relationship affect the household’s application.')
 if kind in {'health','cash'} and re.search(r'disabil|disabled',text):
  conditions.append('If a disability-related pathway may apply, ask about its separate evidence and eligibility requirements.')
 if re.search(r'older|elderly|senior|age 65|age 60',text) and kind not in {'snap','health'}:
  conditions.append('Ask about the age-related pathway or priority noted for this program and which age records are needed.')
 if kind in {'housing','energy','navigation'} and re.search(r'emergency|crisis|shut.?off|eviction',text):
  conditions.append('Explain the emergency and give the date on any notice. The provider needs to know what is happening and the deadline.')
 if kind=='childcare':
  age=re.search(r'(?:under|younger than)\s+(\d{1,2})', ' '.join(g['eligibility']+g['steps']))
  if age:conditions.append(f'The source identifies care for children younger than {age[1]}; check the program’s current age rule and any exceptions before selecting a provider.')
 if kind=='tax' and 'federal earned income' in text:
  conditions.append('The source ties this state credit to federal earned income credit eligibility. Check both returns and the state instructions rather than calculating from income alone.')
 return '<ul>'+''.join('<li>'+E(x)+'</li>' for x in conditions)+'</ul>'


def step_details(g,kind,url,primary):
 text=' '.join(g['steps'])
 lower=text.lower()
 actions=[]
 if kind=='referral':
  actions=[('Start with the local referral service','Dial 211 or use the call, text or online options shown on its website. Check the local operating hours.'),('Describe the household’s needs','Give your location and explain the need and urgency. Ask for providers serving your address.'),('Follow the referral','Save the provider’s contact and intake information, then contact it directly.')]
 elif kind=='crisis':
  actions=[('Choose a contact method','Call or text 988, or use the chat option at the Lifeline website.'),('Explain the concern','You can seek support for yourself or explain your concern for another person. For immediate danger or a medical emergency, call 911.')]
 elif kind=='tax':
  actions=[('Confirm the claim year','Use the revenue agency’s instructions and worksheets for that tax year.'),('Prepare the return or claim','Check the eligibility conditions and complete the required credit form or schedule.'),('File and keep your records','Submit through the agency’s filing process and save the return, worksheets and confirmation.')]
 elif kind in {'wic','weatherization','legal','foodbank','employment','veterans'}:
  actions=[('Find the provider serving you','Use the program website to find its clinic, office, intake service or local partner.'),('Arrange the next step','Ask about appointments, the assessment or intake process and what you need to bring.'),('Complete the provider’s process','Provide the requested information and follow the instructions for the service or application.')]
 else:
  actions=[('Start with the program instructions','Open the listed program website and use its application or intake route for your location.'),('Prepare the household or case information','Gather the relevant records and identify the people, account or service involved in your request.'),('Submit and follow up','Complete the form or intake process, keep confirmation details and respond to any requests from the provider.')]
 if re.search(r'interview',lower) and kind not in {'legal','referral','crisis'}:
  actions.insert(2,('Complete any required interview','The source identifies an interview step. Follow the appointment notice and ask the office how to arrange it if you cannot attend as scheduled.'))
 if re.search(r'landlord.*(?:application|submit|complete)',lower):
  actions.insert(2,('Coordinate with the landlord','The source describes a landlord step. Tell the landlord you are applying and confirm the current participation deadline with the program.'))
 if re.search(r'provider.*(?:participat|approved|takes part)',lower) and kind=='childcare':
  actions.insert(2,('Check the care provider','Confirm that your proposed provider can participate before assuming the care will be funded.'))
 forms=sorted(set(re.findall(r'\b(?:DR\s+\d{4}[A-Z]*|Schedule\s+H(?:-EZ)?|Form\s+\d{4}[A-Z]*)\b',text)))
 if forms and kind=='tax':actions[1]=(actions[1][0],actions[1][1]+' The source names '+', '.join(forms)+'; use the versions and instructions for your claim year.')
 # Only show an extra contact number when the retrieved primary page contains it.
 phones=[]
 for token in re.findall(r'(?<!\d)(?:1[-\s]?)?\(?[2-9]\d{2}\)?[-\s]\d{3}[-\s]\d{4}(?!\d)',text):
  digits=re.sub(r'\D','',token)
  if len(digits)==11 and digits[0]=='1':digits=digits[1:]
  if len(digits)==10 and digits in re.sub(r'\D','',primary) and digits not in phones:phones.append(digits)
 html='<ol class="site-apply-steps">'+''.join('<li><h3 class="pbf-h3">'+E(h)+'</h3>'+paragraphs(body)+'</li>' for h,body in actions)+'</ol>'
 html+=f'<p><a class="pbf-btn pbf-btn--primary" href="{E(url,quote=True)}">Open the program website</a></p>'
 # A number appearing anywhere on a page may be for complaints or fraud reports.
 # Contact details are added through the individually reviewed program notes.
 return html


def specific_questions(g,kind,url):
 text=' '.join(q['question']+' '+q['answer'] for q in g['faqs']).lower()
 options=[]
 if re.search(r'card.*(?:lost|stolen)|lost.*card|replace.*card',text):
  options.append(('What should I do about a missing benefit card?','Use the program’s card customer-service instructions. A card problem is different from a new benefit application; contact the listed card service and ask how to protect the account and request a replacement.'))
 if re.search(r'landlord.*(?:refus|sign)',text):
  options.append(('What if I cannot obtain a landlord signature?','Check the agency’s instructions for that situation before abandoning the claim. Ask which alternative evidence it accepts and keep your rent or housing records.'))
 if re.search(r'breastfeed',text) and kind=='wic':
  options.append(('Where can I ask about breastfeeding support?','Ask your WIC clinic about counseling, referrals and any local support line. Use the program’s current contact information and hours.'))
 if re.search(r'reverse mortgage|hecm',text):
  options.append(('What should I ask about reverse-mortgage counseling?','Ask the housing counselor about the required counseling process, fees and the certificate needed for the specific loan. Use an approved independent counseling provider.'))
 if re.search(r'self.?employ',text):
  options.append(('How should I report self-employment?','Ask which business income and expense records the program requires. Follow its calculation instructions rather than treating gross receipts as the final eligibility figure.'))
 if re.search(r'work requirement|work rules|exempt|exemption',text) and kind in {'snap','cash','health'}:
  options.append(('What if a work rule may not apply to me?','Check the program’s current rules, exemptions and reporting instructions. Explain relevant health, caregiving or other circumstances and ask how to document an exemption.'))
 if kind=='tax' and 'itin' in text:
  options.append(('What if I file with an ITIN?','Check this state credit’s identification rules and the claim-year instructions. Do not assume every state credit uses exactly the same identification rules as the federal credit.'))
 if re.search(r'renter|renters|renting',text) and kind in {'tax','energy','housing'}:
  options.append(('Can a renter ask about this program?','Check the program’s renter rules and required evidence. A utility account, rent certificate or landlord step may matter even when you do not own the property.'))
 return options[:2]


def build():
 guides=json.loads((ROOT/'.content-review/source-guides.json').read_text())
 leads=json.loads((ROOT/'data/source-introductions.json').read_text())
 overrides=json.loads((ROOT/'data/agency-link-overrides.json').read_text())
 notes=json.loads((ROOT/'data/program-editorial-notes.json').read_text())
 output=ROOT/'data/guide-content';output.mkdir(exist_ok=True)
 counts={'preserved':0,'adapted':0};issues=[]
 for g in guides:
  if re.search(r'credit counseling|debt relief|credit repair',g['title'],re.I) or g['slug']=='arizona-nutrition-assistance-snap':continue
  path=output/(g['slug']+'.json')
  if path.exists() and json.loads(path.read_text()).get('status') in {'reviewed','authored'}:counts['preserved']+=1;continue
  kind,profile=choose(g['title'])
  url=overrides.get(g['slug'],{}).get('url',g['agency_url'])
  primary=primary_text(g['agency_url'])
  # User-provided local introductions retain program names, portals and geography.
  lead=leads[g['slug']]
  sentences=re.split(r'(?<=[.!?])\s+(?=[A-Z])',lead)
  safe=[s for s in sentences if not re.search(r'\$|\b\d+(?:\.\d+)?\s*(?:%|percent)|\b20\d{2}\b',s)]
  introduction=' '.join(safe[:2])
  if not introduction: introduction=g['title']+' provides assistance through the listed program or provider. Use its current eligibility and intake instructions.'
  description=(safe[0] if safe else g['title']+': eligibility, application steps and program information.')
  if len(description)>180:description=g['title']+': how to apply, documents to prepare and common questions.'
  faqs=specific_questions(g,kind,url)+profile['faqs']
  if len(faqs)>6:faqs=faqs[:6]
  sources=f'<p>Program information: <a href="{E(url,quote=True)}">the administering agency or provider</a>. Background and historical screenshots: <a href="{E(g["source_url"],quote=True)}">USA Assistance’s program guide</a>.</p>'
  sources+=paragraphs('This guide combines our existing program directory with the source’s program-specific checklist and application topics. Financial figures and other time-sensitive conditions should be checked on the program website. The provider determines eligibility and availability.')
  content={'status':'source-adapted','description':description,'introduction':introduction,'service_type':kind,'sections':{
   'who':source_conditions(g,kind),
   'get':paragraphs(profile['benefit']),
   'docs':document_labels(g,kind),
   'apply':paragraphs(profile['prepare'])+step_details(g,kind,url,primary),
   'after':paragraphs(profile['after']),
   'sources':sources},'faqs':faqs,
   'provenance':{'local_intro':g['slug'],'source_url':g['source_url'],'source_updated':g['source_updated'],'primary_url':url,'primary_retrieved':bool(primary),'facts_verified':False,'adapted_on':'2026-10-01'}}
  note=notes.get(g['slug'])
  if note:
   if note.get('introduction'):content['introduction']=note['introduction']
   for section,body in note.get('sections',{}).items():content['sections'][section]=body
   for section,body in note.get('append',{}).items():content['sections'][section]+=body
   content['faqs']=note.get('faqs',[])+content['faqs']
   content['faqs']=content['faqs'][:6]
   content['provenance']['primary_notes_reviewed_on']='2026-10-01'
   content['provenance']['primary_notes_url']=note['url']
  path.write_text(json.dumps(content,indent=2,ensure_ascii=False)+'\n');counts['adapted']+=1
  if not primary:issues.append({'slug':g['slug'],'url':url,'issue':'Primary-page retrieval unavailable; source adaptation is not agency verification.'})
 (ROOT/'.content-review/remaining-primary-review.json').write_text(json.dumps(issues,indent=2)+'\n')
 print(counts,'primary retrieval gaps:',len(issues))

if __name__=='__main__':build()
