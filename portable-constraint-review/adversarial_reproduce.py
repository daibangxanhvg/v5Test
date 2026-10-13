import pathlib,json,tempfile,sys,itertools
from portable_constraints import verifier_a as A,verifier_b as B
from portable_constraints.runtime import Runtime
from portable_constraints.package import digest,canonical
M=pathlib.Path('modules')
def t(label,mid,c,a,f=None,d=M):
 v=[]
 for ev in [A.evaluate,B.evaluate]:
  try:v.append(Runtime(d,ev).decide(mid,c,a,f))
  except Exception as e:v.append(type(e).__name__)
 if label:print(label,v)
 return v
g=[{'acceptable_skus':['A','B'],'qty':1},{'acceptable_skus':['A'],'qty':1}];a={'line_items':[{'sku':'A','qty':1},{'sku':'B','qty':1}]}
t('overlap','checkout_matching',{'requirements':g},a);t('reorder','checkout_matching',{'requirements':g[::-1]},a)
for q in [1.9,float('inf')]:t('qty '+str(q),'checkout_matching',{'requirements':[{'acceptable_skus':['A'],'qty':q}]},a)
for lines in [[{'sku':'A','qty':1},{'sku':'A','qty':0}],[{'sku':'A','qty':0},{'sku':'A','qty':1}],[None]]:t('duplicates/malformed '+str(lines),'checkout_matching',{'requirements':[{'acceptable_skus':['A'],'qty':1}]},{'line_items':lines})
t('negative duration','calendar_duration',{'max_minutes':1},{'start_minute':100,'end_minute':0})
t('string arithmetic','payment_monthly_budget',{'budget':'9'},{'amount':'0'},{'spent_this_month':'100'})
t('negative spend','payment_monthly_budget',{'budget':100},{'amount':1000},{'spent_this_month':-1000})
t('null identity','document_ownership',{}, {'file_id':'f'},{'owner_team_by_file':{'f':None},'requester_team':None})
for f in [{},{'room_membership':{'r':True}},{'room_membership':{'r':1}}]:t('facts '+str(f),'matrix_membership',{}, {'room_id':'r'},f)
t('extra facts','calendar_duration',{'max_minutes':1},{'start_minute':0,'end_minute':1},{'x':1})
t('Unicode','document_ownership',{}, {'file_id':'é'},{'owner_team_by_file':{'e\u0301':'A'},'requester_team':'A'})
print('canonical',canonical(-0.0),canonical(0.0),canonical(float('nan')))
class D(dict):pass
t('subclass divergence','calendar_duration',{'max_minutes':1},D(start_minute=0,end_minute=1))
with tempfile.TemporaryDirectory() as d:
 p=json.loads((M/'calendar_duration.json').read_text())
 def save(program):
  p.update(id='other',version='unsupported',schema=None,program=program);p['digest']=digest({k:v for k,v in p.items() if k!='digest'});pathlib.Path(d,'calendar_duration.json').write_text(json.dumps(p))
 save({'const':True});t('substitution','calendar_duration',{}, {},d=d)
 base=pathlib.Path(d)/'modules';base.mkdir()
 t('traversal','../calendar_duration',{}, {},d=base)
 save({'lte':[]});t('arity','calendar_duration',{}, {},d=d)
 save({'and':[{'const':False},{'unknown':True}]});t('unvisited opcode','calendar_duration',{}, {},d=d)
 old=sys.getrecursionlimit();sys.setrecursionlimit(10000);n={'const':True}
 for _ in range(1500):n={'and':[n]}
 save(n);sys.setrecursionlimit(old);t('depth','calendar_duration',{}, {},d=d)
def oracle(gs,stock,i=0):
 if i==len(gs):return True
 for s in gs[i]:
  if stock[s]:
   q=dict(stock);q[s]-=1
   if oracle(gs,q,i+1):return True
 return False
count=bad=0
for n in range(1,5):
 for gs in itertools.product([['A'],['B'],['A','B']],repeat=n):
  for ca,cb in itertools.product(range(3),repeat=2):
   v=t(None,'checkout_matching',{'requirements':[{'acceptable_skus':x,'qty':1} for x in gs]},{'line_items':[{'sku':'A','qty':ca},{'sku':'B','qty':cb}]});e=oracle(gs,{'A':ca,'B':cb});count+=1;bad+=v!=[e,e]
print('oracle cases/mismatches',count,bad)
vals=[None,False,True,-1,0,1,1.9,10**100,float('inf'),float('nan'),'1','é',[],{},[1]];count=diff=crash=0
for x,y in itertools.product(vals,repeat=2):
 for mid,c,a,f in [('calendar_duration',{'max_minutes':1},{'start_minute':x,'end_minute':y},{}),('payment_monthly_budget',{'budget':1},{'amount':x},{'spent_this_month':y})]:
  v=t(None,mid,c,a,f);count+=1;diff+=v[0]!=v[1];crash+=any(isinstance(z,str) for z in v)
print('differential cases/divergences/crashes',count,diff,crash)

import time
for size in [1000,10000,100000]:
 start=time.monotonic()
 v=t(None,'checkout_matching',{'requirements':[{'acceptable_skus':['A'],'qty':1}]},{'line_items':[{'sku':'A','qty':1}]*size})
 print('large input',size,v,round(time.monotonic()-start,4))
