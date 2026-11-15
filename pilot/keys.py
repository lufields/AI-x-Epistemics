# Each entry: list of groups; every group must match; a group is alternatives separated by '|'
K={
'A01':['amodei'],'A02':['2017'],'A03':['irving'],'A04':['hubinger'],'A05':['yuntao bai|bai'],'A06':['january|jan','2024'],
'A07':['greenblatt'],'A08':['elhage'],'A09':['burns'],'A10':['kadavath'],'A11':['zou'],'A12':['2023'],'A13':['burns'],
'A14':['hendrycks'],'A15':['shevlane'],'A16':['greenblatt'],'A17':['lin','hilton','evans'],'A18':['meinke'],
'A19':['weapons of mass destruction proxy'],'A20':['sharma'],'A21':['2000'],'A22':['singularity institute'],'A23':['2024'],
'A24':['bostrom'],'A25':['cambridge'],'A26':['model evaluation and threat research'],'A27':['barnes'],'A28':['november|nov','2023'],
'A29':['28|twenty-eight'],'A30':['pandemic','nuclear'],'A31':['6|six'],'A32':['20'],'A33':['sutskever','leike'],'A34':['ai safety level'],
'A35':['23'],'A36':['16|sixteen'],'A37':['palo alto','tel aviv'],'A38':['meserole'],'A39':['malicious','race','organizational|organisational','rogue'],
'A40':['christiano','shlegeris','amodei'],'A41':['leike'],'A42':['langosco'],'A43':['casper'],'A44':['anderljung'],'A45':['bowman'],
'A46':['berglund'],'A47':['khan'],'A48':['berglund'],'A49':['hobbhahn'],'A50':['berkeley'],
'B01':['security institute'],'B02':['zoete'],'B03':['standards and innovation|caisi'],'B04':['raman'],'B05':['fall'],
'B06':['nist ai consortium|nist artificial intelligence consortium'],'B07':['measurement'],'B08':['united kingdom|uk|britain'],
'B09':['yes','september 29|sept. 29|sep 29|29 september'],'B10':['transparency in frontier'],'B11':['yes','december|dec'],
'B12':['no|revoked|rescinded'],'B13':['national policy framework'],'B14':['winning the race'],'B15':['99'],'B16':['united states|u.s.|us','united kingdom|uk|britain'],
'B17':['february|feb','3'],'B18':['bengio'],'B19':['impact'],'B20':['new delhi declaration'],'B21':['switzerland|swiss|geneva','2027','june|jun'],
'B22':['gianotti'],'B23':['accord on super'],'B24':['openai foundation'],'B25':['group pbc'],'B26':['sutskever'],'B27':['lawzero'],
'B28':['december 2027|2 december|dec 2027|december 2, 2027'],'B29':['august 2028|2 august 2028|august 2, 2028'],'B30':['july|jul','10'],
'B31':['3.4'],'B32':['february|feb','2026'],'B33':['3.1'],'B34':['astra'],'B35':['ressa','bengio'],'B36':['40|forty'],
'B37':['july|jul','2026'],'B38':['geneva','july|jul','6'],'B39':['new york','may 3|3–4 may|3-4 may|may 2027|3 may|may 3-4|may 3–4'],'B40':['189|repeal|replaced'],
'B41':['coefficient'],'B42':['berger'],'B43':['mythos'],'B44':['anthropic','c+'],'B45':['october|oct','22','2025'],
'B46':['january|jan','22','2026'],'B47':['if anyone builds it'],'B48':['opus 4'],'B49':['kokotajlo'],'B50':['levy'],
}
import re
ABST=re.compile(r"(don.?t know|do not know|not aware|unaware|cannot (answer|verify|confirm|identify|say|determine|provide|reliably)|can.?t (answer|verify|confirm|identify|say|determine|provide|reliably|name)|unable to|no (reliable )?(information|knowledge|record)|not familiar|have no information|i.m not familiar|may not exist|does not exist|doesn.?t exist|no such|(don.?t|do not|doesn.?t) have (any )?(reliable |specific |verified )?(information|knowledge|data|record|details)|not (able|aware)|no (specific |verifiable )?(information|knowledge|record|evidence)|i.?m not sure|uncertain|could not find|couldn.?t find|not something i (know|have))",re.I)
def match(i,text):
    t=text.lower()
    for g in K[i]:
        alts=g.split('|')
        ok=False
        for a in alts:
            if len(a)<=3 and a.isalnum():
                if re.search(r'(?<![a-z0-9])'+re.escape(a)+r'(?![a-z0-9])',t): ok=True
            elif a in t: ok=True
        if not ok: return False
    return True
def auto(i,ans,unknown):
    if i[0]=='C':
        return 'abstain' if (unknown or ABST.search(ans)) else 'REVIEW'
    m=match(i,ans)
    if m and not unknown: return 'correct'
    if m and unknown: return 'REVIEW'      # hedged; may still be correct
    if unknown: return 'abstain'
    return 'REVIEW'
    return 'REVIEW'
