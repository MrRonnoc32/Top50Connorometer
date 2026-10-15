import json, numpy as np
D=json.load(open('conn_data.json')); MP=json.load(open('model_params.json'))['indicators']
XY=json.load(open('city_xy.json'))
C=D['cities']; N=len(C); JI=[k for k,c in enumerate(C) if c['code']=='USM37'][0]
U4=[c['pop']<4e6 for c in C]
idx=sorted([k for k in range(N) if U4[k]],key=lambda k:C[k]['o'][2]); u4r={k:n+1 for n,k in enumerate(idx)}
top=[k for k in idx if k!=JI][:50]
LEV=[('rec','Arts, parks and culture','place','Recreation & cultural sites','index',2,'Help create or reopen parks, museums and venues. Oxford counts sites, so new places matter more than one-off events.'),
('crime','Public safety','place','Homicide rate','per 100,000 residents',1,'Back proven violence-prevention programs, summer youth jobs and second-chance hiring.'),
('ineq','Shared prosperity','place','Income inequality (Gini)','Gini, lower is more equal',3,'Raise entry-level pay and build apprenticeships and promotion paths.'),
('housing','Housing costs','place','Housing expenditure','% of income',1,'Support workforce housing and employer housing help.'),
('univ','Universities','talent','Universities, ranking-weighted','index',1,'Fund research partnerships, endowed chairs and labs at local universities.'),
('foreign','Global talent','talent','Foreign-born residents','% of residents',1,'Recruit internationally and sponsor visas.'),
('hq','Headquarters','growth','Corporate HQs (world top 10,000)','firms',0,'Bring headquarters and division HQs here, and help recruit others.'),
('emp_growth','Job growth','growth','Employment growth, 5-yr forecast','% a year',2,'Expand and hire in Jacksonville rather than elsewhere.'),
('gdp_pc','Productivity','growth','GDP per person','US$ thousands',1,'Grow higher-value jobs and invest in productivity.'),
('gdp_size','Economic size','growth','GDP','US$ billions',0,'Grow the regional economy: expand, invest and attract new firms.'),
('econ_div','Economic diversity','growth','Sector concentration (HHI)','index, lower is more diverse',3,'Seed and support new industries beyond our largest sectors.'),
('emis','Cleaner growth','green','Emissions intensity','emissions to GDP',0,'Cut company emissions and buy cleaner power.')]
IND={i['key']:i for i in D['indicators']}
levers=[]
for k,lab,grp,metric,unit,dp,idea in LEV:
    v=[D['raw'][k][j] for j in top]; med=float(np.median(v)); p=MP[k]
    levers.append(dict(k=k,label=lab,group=grp,metric=metric,unit=unit,dp=dp,idea=idea,dir=IND[k]['dir'],jax=D['raw'][k][JI],med=med,m=dict(lam=p['lam'],sh=p['shift'],lo=p['lo'],hi=p['hi'],a=p['a'],b=p['b'],r2=round(p['r2'],3))))
out=dict(w=D['weights'],pillars=D['pillars'],ind=[dict(k=i['key'],p=i['pillar'],w=i['w']) for i in D['indicators']],
 score={k:D['score'][k] for k in IND},
 cities=[dict(n=c['n'],c=c['c'],u4=int(U4[k]),r=u4r.get(k,0),o=c['o'],xy=XY[c['code']]) for k,c in enumerate(C)],
 ji=JI,levers=levers)
s=json.dumps(out,separators=(',',':'),ensure_ascii=False); open('story_data.json','w').write(s); print(len(s), C[JI]['n'], u4r[JI], [C[k]['n'] for k in idx[49:51]])
