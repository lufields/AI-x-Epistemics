# v2 runner: each question is sent as its own conversation (the model never sees the other two questions about the same concept).
import json, sys, os, concurrent.futures as cf
import run   # reuses call() and the key; COND must be "natural"
SYS="Today's date is November 14, 2026."
BREV=os.environ.get('BREV','0')=="1"
SUFFIX=("\n\nAnswer in at most three sentences." if BREV else "")+"\n\nHow confident are you that your answer is correct? Give a number from 0 to 100."
def call(model,q):
    run.PROMPT=SYS; run.NAT_SUFFIX=SUFFIX; run.COND="natural"
    return run.call(model,q)
if __name__=="__main__":
    model=sys.argv[1]; tag=os.environ.get('TAG','rep1')
    qs=[json.loads(l) for l in open('data/questions_v2.jsonl')]
    if os.environ.get('CIDS'): qs=[q for q in qs if q['cid'] in os.environ['CIDS'].split(',')]
    out=f"data/raw_v2/{tag}/{model.replace('/','_')}.jsonl"; os.makedirs(os.path.dirname(out),exist_ok=True)
    done=set()
    if os.path.exists(out):
        for l in open(out):
            d=json.loads(l)
            if 'error' not in d['resp']: done.add(d['qid'])
    qs=[q for q in qs if q['qid'] not in done]
    with cf.ThreadPoolExecutor(int(os.environ.get("THREADS","2"))) as ex, open(out,'a') as f:
        futs={ex.submit(call,model,q['question']):q for q in qs}
        for fu in cf.as_completed(futs):
            q=futs[fu]; r=fu.result()
            f.write(json.dumps({"qid":q['qid'],"model":model,"brev":BREV,"prompt_suffix":SUFFIX,"resp":r})+"\n"); f.flush()
    print(model,tag,"done",len(qs))
