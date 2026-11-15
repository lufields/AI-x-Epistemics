# Figure 1: invented terms treated as real, by question framing and model (pooled over repetitions, Wilson 95% CI).
import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from stats import wilson
R=json.load(open('v2_rows.json'))
models=['Fable 5.2','GPT-6 Astra','Gemini 4 Argon']; col={'Fable 5.2':'#2a78d6','GPT-6 Astra':'#eb6834','Gemini 4 Argon':'#1baf7a'}
qts=[('definition','Definition\n"What does X refer to?"'),('case','Application\n"Is this an example of X?"'),('importance','Importance (false premise)\n"Why is X a risk / important?"')]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#52514e','axes.labelcolor':'#0b0b0b','xtick.color':'#52514e','ytick.color':'#52514e'})
fig,ax=plt.subplots(figsize=(6.5,3.0),dpi=300); fig.patch.set_facecolor('white')
w=0.26
for i,m in enumerate(models):
    for j,(qt,_) in enumerate(qts):
        s=[r for r in R if not r['real'] and r['qtype']==qt and r['model']==m and r['grade']]
        k=sum(r['grade'] in('fabricates','hedges') for r in s); ks=sum(r['grade']=='fabricates' for r in s); n=len(s)
        p,lo,hi=wilson(k,n); ps=ks/n if n else 0
        x=j+(i-1)*(w+0.02)
        ax.bar(x,100*p,w,color=col[m],alpha=0.35,edgecolor='white',linewidth=1, label=None)
        ax.bar(x,100*ps,w,color=col[m],edgecolor='white',linewidth=1,label=m if j==0 else None)
        ax.errorbar(x,100*p,yerr=[[100*(p-lo)],[100*(hi-p)]],color='#52514e',lw=0.8,capsize=2)
        ax.text(x,100*hi+2,f"{100*p:.0f}",ha='center',va='bottom',fontsize=7.5,color='#0b0b0b')
ax.set_xticks(range(3)); ax.set_xticklabels([l for _,l in qts],fontsize=8)
ax.set_ylim(0,112); ax.set_yticks([0,25,50,75,100]); ax.set_ylabel('% of answers treating the\ninvented term as real')
ax.yaxis.grid(True,color='#e6e5e0',lw=0.6); ax.set_axisbelow(True)
from matplotlib.patches import Patch
h=[Patch(color=col[m],label=m) for m in models]+[Patch(facecolor='#999',alpha=0.35,label='+ hedged ("not standardized", "if you mean")')]
ax.legend(handles=h,frameon=False,fontsize=7.5,ncol=4,loc='upper center',bbox_to_anchor=(0.5,1.13))
n=len([r for r in R if not r['real'] and r['qtype']=='definition' and r['model']=='Fable 5.2' and r['grade']])
plt.tight_layout(); plt.savefig('fig1.png',dpi=300,bbox_inches='tight'); print('n per bar',n)
