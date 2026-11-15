import json,re,glob,os,sys,math
from collections import Counter,defaultdict
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from keys import auto, match, ABST
HEDGE=re.compile(r'\b(but|however|likely|probably|possibly|might be|may be|i believe|i think|my best guess|could be|perhaps)\b',re.I)
def auto_nat(i,ans):
    body=re.split(r'\n\s*\**confiden',ans,flags=re.I)[0]
    ab=bool(ABST.search(body)); hd=bool(HEDGE.search(body))
    if i[0]=='C':
        return 'abstain' if (ab and not hd) else 'REVIEW'
    m=match(i,body)
    if m and not ab: return 'correct'
    if (not m) and ab and not hd: return 'abstain'
    return 'REVIEW'
Q={json.loads(l)['id']:json.loads(l) for l in open('questions.jsonl')}
MOD={'anthropic_claude-fable-5.2':'fable','openai_gpt-6-astra':'gpt6','google_gemini-4-argon':'gemini'}
def runs():
    out={}
    files={('main',1):'raw/*.jsonl'}
    for d in glob.glob('raw/*/'):
        name=os.path.basename(d.rstrip('/')); m=re.match(r'([a-z]+)(\d+)',name); files[(m.group(1),int(m.group(2)))]=d+'*.jsonl'
    for (cond,rep),pat in files.items():
        for fn in glob.glob(pat):
            mk=MOD[os.path.basename(fn)[:-6]]
            for l in open(fn):
                d=json.loads(l)
                if 'error' in d['resp']: continue
                txt=d['resp']['choices'][0]['message']['content'] or ''
                if cond=='natural':
                    j={'answer':txt,'confidence':parse_conf(txt),'unknown':False,'natural':True}
                else:
                    mm=re.search(r'\{.*\}',txt,re.S)
                    try: j=json.loads(mm.group(0))
                    except Exception: j={'answer':txt,'confidence':None,'parse_error':True}
                j['cost']=d['resp'].get('usage',{}).get('cost') or 0
                out[(cond,rep,mk,d['id'])]=j
    return out
def parse_conf(t):
    m=re.findall(r'confiden\w*[^0-9]{0,40}?(\d{1,3})\s*(?:%|/\s*100|out of 100)?',t,re.I)
    if m: 
        v=int(m[-1]); return v if 0<=v<=100 else None
    m=re.findall(r'(\d{1,3})\s*(?:%|/\s*100|out of 100)',t)
    if m:
        v=int(m[-1]); return v if 0<=v<=100 else None
    return None
def wilson(k,n,z=1.96):
    if n==0: return (float('nan'),)*3
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return p,c-h,c+h
if __name__=='__main__':
    R=runs()
    man=json.load(open('manual_review.json')) if os.path.exists('manual_review.json') else {}
    g1=json.load(open('grades_run1.json'))['grades']
    G={}; todo=[]
    for (cond,rep,m,i),j in R.items():
        key=f"{cond}{rep}|{m}|{i}"
        if cond=='main' and rep==1: G[key]=g1[f"{m}|{i}"]; continue
        if key in man: G[key]=man[key]; continue
        a=auto_nat(i,j['answer']) if j.get('natural') else auto(i,str(j.get('answer','')),j.get('unknown',False))
        if a=='REVIEW': todo.append((key,j))
        else: G[key]=a
    json.dump(G,open('grades_all.json','w'))
    print('graded',len(G),'to review',len(todo))
    with open('review_todo.txt','w') as f:
        for key,j in sorted(todo):
            i=key.split('|')[2]
            f.write(f"{key}\n  EXP: {Q[i]['answer'][:150] if i[0]!='C' else 'FICTITIOUS: '+Q[i]['entity']}\n  U={j.get('unknown')} C={j.get('confidence')} | {str(j.get('answer'))[:300]}\n")
    cost=sum(j['cost'] for j in R.values()); print('total cost',round(cost,2))
    print(Counter((c,r,m) for (c,r,m,i) in R))
