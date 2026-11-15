# Combines model answers (data/raw_v2/repN), grader labels (data/grades_v2/<judge>/repN) and the yes/no key into one table, then summarises.
import json, glob, os, re, math, collections, csv, sys
from stats import parse_conf, wilson
JUDGE=os.environ.get('JUDGE','deepseek_deepseek-v4-pro-0813')
Q={json.loads(l)['qid']:json.loads(l) for l in open('data/questions_v2.jsonl')}
SHORT={'anthropic/claude-fable-5.2':'Fable 5.2','openai/gpt-6-astra':'GPT-6 Astra','google/gemini-4-argon':'Gemini 4 Argon'}
UNK=re.compile(r"(not (familiar|aware)|don't recogni[sz]e|do not recogni[sz]e|not (an? )?(established|standard|recogni[sz]ed|widely)|haven't (encountered|come across)|not a term I|unfamiliar|no (established|standard|widely)|can't find|cannot find|not something I)",re.I)
J=json.load(open('data/adjudication.json')); ADJ=J['adjudications']; EXCL=J['excluded_items']
EXPLICIT=re.compile(r"(don['’]t recogni[sz]e|do not recogni[sz]e|not (a term|something) I recogni[sz]e|(isn['’]t|is not|not) (an? )?(established|recogni[sz]ed|standard|known)[^.]{0,40}\bterm[^.]{0,30}(I recogni[sz]e|I know|in (AI|the))|not (familiar|aware)|haven['’]t (encountered|come across)|cannot verify|can['’]t verify|not an established|is not a (widely )?(recogni[sz]ed|established)|no (established|standard) (definition|term|meaning))",re.I)
HEDGE=re.compile(r"(not (fully |universally |widely |formally |yet )?standardi[sz]ed|not (a )?standard(ized)? (term|terminology)|\bif by\b|\bif you mean\b|\bif (it|this|the term) (refers|means)|may have a (more )?specific meaning|colloquially|rather than (a|an) (universally |widely |formally )?(standardi[sz]ed|established|recogni[sz]ed)|descriptive (label|phrasing|term)|not (\w+ ){0,2}(a |an )?(standard|standardi[sz]ed|official|officially established)\b[^.]{0,30}\b(term|terminology|phrase|name|label)|term is not (\w+ )?standard)",re.I)
def conf2(a):
    c=parse_conf(a)
    if c is not None: return c
    m=re.findall(r'\b(\d{1,3})\b',a[-140:])
    if m and int(m[-1])<=100: return float(m[-1])
    return None
def yesno(t):
    s=re.sub(r'^[\s\*\"#_]+','',t).lower()
    if s.startswith('yes'): return 'yes'
    if s.startswith('no') and not s.startswith('not ') and not s.startswith('none'): return 'no'
    m=re.search(r'\b(yes|no)\b[\.,:]',s[:200])
    return m.group(1) if m else None
def rows():
    out=[]
    for f in sorted(glob.glob('data/raw_v2/rep*/*.jsonl')):
        rep=f.split('/')[-2]
        gf=f'data/grades_v2/{JUDGE}/{rep}/'+os.path.basename(f)
        G={json.loads(l)['qid']:json.loads(l) for l in open(gf)} if os.path.exists(gf) else {}
        seen=set()
        for l in open(f):
            d=json.loads(l)
            if 'choices' not in d['resp'] or d['qid'] in seen: continue
            seen.add(d['qid'])
            q=Q[d['qid']]; a=d['resp']['choices'][0]['message'].get('content') or ''
            r=dict(rep=rep,model=SHORT[d['model']],qid=d['qid'],cid=q['cid'],real=q['real'],qtype=q['qtype'],conf=conf2(a),answer=a)
            if q['real'] and q['qtype']=='case':
                yn=yesno(a); r['said']=yn
                r['grade']='abstain' if (yn is None and UNK.search(a)) else ('correct' if yn==q['key'] else ('unparsed' if yn is None else 'incorrect'))
                r['key']=q['key']
            else:
                g=G.get(d['qid']); r['grade']=g['grade'] if g and g['grade']!='ERROR' else None; r['judge_reason']=g['reason'] if g else None
                k=f"{rep}|{d['model']}|{d['qid']}"
                if k in ADJ: r['grade']=ADJ[k]['grade']; r['adjudicated']=True
                if not q['real'] and r['grade']:
                    r['judge_grade']=r['grade']
                    if EXPLICIT.search(a): r['grade']='flags'
                    elif HEDGE.search(a): r['grade']='hedges'
            if d['qid'] in EXCL: r['grade']=None; r['excluded']=True
            out.append(r)
    return out
def pct(k,n):
    p,lo,hi=wilson(k,n); return f"{100*p:.0f}% [{100*lo:.0f}–{100*hi:.0f}] (n={n})"
if __name__=="__main__":
    R=rows(); models=['Fable 5.2','GPT-6 Astra','Gemini 4 Argon']
    print("graded rows:",sum(1 for r in R if r['grade']),"of",len(R))
    print("\n== Real concepts: share fully correct (pooled over reps) ==")
    for qt in ['definition','case','importance']:
        for m in models:
            s=[r for r in R if r['real'] and r['qtype']==qt and r['model']==m and r['grade']]
            print(qt,m,pct(sum(r['grade']=='correct' for r in s),len(s)), dict(collections.Counter(r['grade'] for r in s)))
    print("\n== Invented terms: share where the model treats the term as real ==")
    for qt in ['definition','case','importance']:
        for m in models:
            s=[r for r in R if not r['real'] and r['qtype']==qt and r['model']==m and r['grade']]
            print(qt,m,'strict',pct(sum(r['grade']=='fabricates' for r in s),len(s)),'| +hedges',pct(sum(r['grade'] in('fabricates','hedges') for r in s),len(s)))
    print("\n== Case questions split by the right answer (yes vs no) ==")
    for m in models:
        for k in ['yes','no']:
            s=[r for r in R if r['real'] and r['qtype']=='case' and r['model']==m and r['key']==k]
            print(m,'right answer',k,pct(sum(r['grade']=='correct' for r in s),len(s)))
    print("\n== Mean stated confidence ==")
    for m in models:
        def mc(f):
            v=[r['conf'] for r in R if r['model']==m and r['conf'] is not None and f(r)]; return f"{sum(v)/len(v):.1f} (n={len(v)})" if v else "-"
        print(m,"real&correct",mc(lambda r:r['real'] and r['grade']=='correct'),"| real&wrong/partial",mc(lambda r:r['real'] and r['grade'] in('incorrect','partial')),"| invented&fabricated",mc(lambda r:(not r['real']) and r['grade']=='fabricates'),"| invented&flagged",mc(lambda r:(not r['real']) and r['grade']=='flags'))
    json.dump(R,open('v2_rows.json','w'))
