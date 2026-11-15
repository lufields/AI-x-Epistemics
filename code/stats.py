import re, math
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
