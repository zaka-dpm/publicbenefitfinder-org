"""Summarize authored content without treating generated pages as finished articles."""
import json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def build():
 catalog=json.loads((ROOT/'data/finder-programs.json').read_text())['states']
 articles={p.stem:json.loads(p.read_text()) for p in (ROOT/'data/guide-content').glob('*.json')}
 articles['arizona-nutrition-assistance-snap']={'status':'reviewed'}
 states=[]
 for state in catalog:
  counts=Counter(articles.get(p['slug'],{}).get('status','missing') for p in state['programs'])
  remaining=[p['slug'] for p in state['programs'] if articles.get(p['slug'],{}).get('status') not in {'reviewed','authored'}]
  blockers=[{'slug':p['slug'],'issues':articles[p['slug']].get('provenance',{}).get('blockers',articles[p['slug']].get('provenance',{}).get('review_blockers',articles[p['slug']].get('review_blockers',[])))} for p in state['programs'] if articles.get(p['slug'],{}).get('status')=='authored']
  states.append({'state':state['name'],'slug':state['slug'],'programs':len(state['programs']),'statuses':dict(counts),'rewriting_remaining':remaining,'pending_primary_review':blockers})
 totals=Counter(a.get('status','missing') for a in articles.values())
 report={'updated':'2026-10-01','guide_count':len(articles),'statuses':dict(totals),'fully_reviewed_states':[s['state'] for s in states if s['statuses'].get('reviewed',0)==s['programs']],'states':states,'publication':'Local only. No push authorized.'}
 (ROOT/'data/content-progress.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:report[k] for k in ['guide_count','statuses','fully_reviewed_states']},indent=2))
if __name__=='__main__':build()
