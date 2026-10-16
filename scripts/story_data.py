import json, numpy as np
D=json.load(open('conn_data.json')); MP=json.load(open('model_params.json'))['indicators']
XY=json.load(open('city_xy.json')); PR=json.load(open('progress.json'))
C=D['cities']; N=len(C); JI=[k for k,c in enumerate(C) if c['code']=='USM37'][0]
U4=[c['pop']<4e6 for c in C]
idx=sorted([k for k in range(N) if U4[k]],key=lambda k:C[k]['o'][2]); u4r={k:n+1 for n,k in enumerate(idx)}
top=[k for k in idx if k!=JI][:50]
# Who controls each indicator: L = local, S = regional or state, N = national, X = not actionable.
# (key, label, control, metric, unit, dp, idea)
LEV=[
('gdp_size','Economic size','L','GDP','US$ billions',0,'Grow the regional economy: expand, invest and attract new firms.'),
('gdp_growth','Economic growth outlook','L','GDP growth, 5-yr forecast','% a year',2,'Invest and expand here. Oxford\'s forecast follows the industries and investment the region attracts.'),
('econ_stab','Economic stability','X','Swings in yearly growth','std. dev.',2,'Mostly set by the national business cycle. Shown so you can see its weight.'),
('gdp_pc','Productivity','L','GDP per person','US$ thousands',1,'Grow higher-value jobs and invest in productivity.'),
('emp_growth','Job growth','L','Employment growth, 5-yr forecast','% a year',2,'Expand and hire in Jacksonville rather than elsewhere.'),
('econ_div','Economic diversity','L','Sector concentration (HHI)','index, lower is more diverse',3,'Seed and support new industries beyond our largest sectors.'),
('pop_growth','Population growth','L','Population growth','% a year',2,'Recruit talent from other regions, and back housing supply so people can move here.'),
('age','Age profile','X','Old-age ratio','% of working-age',1,'Set by long-run demographics. Shown so you can see its weight.'),
('univ','Universities','L','Universities, ranking-weighted','index',1,'Fund research partnerships, endowed chairs and labs at local universities.'),
('hq','Headquarters','L','Corporate HQs (world top 10,000)','firms',0,'Bring headquarters and division HQs here, and help recruit others.'),
('edu','Educational attainment','S','Education index','0 to 1',3,'Measured for Florida as a whole, so local gains barely register.'),
('foreign','Global talent','L','Foreign-born residents','% of residents',1,'Recruit internationally and sponsor visas.'),
('ineq','Shared prosperity','L','Income inequality (Gini)','Gini, lower is more equal',3,'Raise entry-level pay and build apprenticeships and promotion paths.'),
('inc_pc','Income per person','L','Income per person','PPP$ thousands',1,'Pay and promotion paths that raise incomes across the workforce.'),
('housing','Housing costs','L','Housing expenditure','% of income',1,'Support workforce housing and employer housing help.'),
('life','Life expectancy','S','Life expectancy index','0 to 1',3,'Measured for Florida as a whole, so local gains barely register.'),
('crime','Public safety','L','Homicide rate','per 100,000 residents',1,'Back proven violence-prevention programs, summer youth jobs and second-chance hiring.'),
('rec','Arts, parks and culture','L','Recreation & cultural sites','index',3,'Help create or reopen parks, museums and venues. Oxford counts sites, so new places matter more than one-off events.'),
('air','Air quality','S','Fine particles (PM2.5)','µg/m³',1,'Cut fleet and facility emissions and support cleaner transport. Air moves across the region.'),
('emis','Cleaner growth','L','Emissions intensity','emissions to GDP',0,'Cut company emissions and buy cleaner power.'),
('disaster','Natural disasters','X','Hazard index','index',1,'Set by geography. Resilience spending helps people but doesn\'t change this score.'),
('temp','Temperature anomalies','X','Temperature anomaly, 10-yr average','°C',2,'Set by climate. Shown so you can see its weight.'),
('rain','Rainfall anomalies','X','Rainfall anomaly (SPI)','index',2,'Set by climate. Shown so you can see its weight.'),
('inst','Institutions','N','Institutions index','index',1,'Set for the whole United States.'),
('polstab','Political stability','N','Political stability index','index',1,'Set for the whole United States.'),
('busenv','Business environment','N','Business environment index','index',2,'Set for the whole United States.'),
('civlib','Civil liberties','N','Civil liberties index','index',0,'Set for the whole United States.')]
IND={i['key']:i for i in D['indicators']}
assert set(IND)=={l[0] for l in LEV}, set(IND)^{l[0] for l in LEV}
r4=lambda x: float('%.4g'%x)
US=[k for k in range(N) if C[k]['us']]
def near(k, v, pool, n=3):
    return [C[j]['n'] for j in sorted(pool, key=lambda j: abs(D['raw'][k][j]-v))[:n]]
levers=[]
for k,lab,ctrl,metric,unit,dp,idea in LEV:
    v=np.array([D['raw'][k][j] for j in top]); d=IND[k]['dir']; med=float(np.median(v)); jax=D['raw'][k][JI]
    behind = (jax<med) if d>0 else (jax>med)
    tgt = med if behind else float(np.percentile(v, 90 if d>0 else 10))
    if not behind and ((d>0 and tgt<=jax) or (d<0 and tgt>=jax)): tgt=float(v.max() if d>0 else v.min())
    p=MP[k]
    levers.append(dict(k=k,label=lab,p=IND[k]['pillar'],ctrl=ctrl,metric=metric,unit=unit,dp=dp,idea=idea,dir=d,jax=jax,med=tgt,
      tgtLab='Top 50 typical' if behind else 'Best tenth of the Top 50', ahead=not behind, rough=p['r2']<0.95,
      m=dict(lam=p['lam'],sh=p['shift'],lo=p['lo'],hi=p['hi'],a=p['a'],b=p['b'],r2=round(p['r2'],3))))
# raw values for the "in real life" lines (cities under 4M plus US cities), to 4 significant figures
RAWK=['rec','crime','housing','inc_pc']
raw={k:[r4(x) for x in D['raw'][k]] for k in RAWK}
# "In real life" templates: computed facts (filled on the page) plus one researched example each
low_us=sorted(US,key=lambda j:D['raw']['crime'][j])[:3]
real={
 'rec':dict(osm='In our OpenStreetMap count, Jacksonville had about 5 museums, galleries and theaters per 100,000 residents. Eindhoven, now 50th, had 21 to 34.',
   usmax=[C[j]['n'] for j in sorted([j for j in US if U4[j] and j!=JI],key=lambda j:-D['raw']['rec'][j])[:2]],
   usmaxv=r4(max(D['raw']['rec'][j] for j in US if U4[j] and j!=JI)),
   ex=dict(city='Oklahoma City',text='Oklahoma City voters approved MAPS 4 in December 2019: a temporary one-cent sales tax expected to raise about $1.1 billion over eight years (2020 to 2028). It includes $154 million for parks, plus money for arenas, a stadium and a civil rights center. It follows earlier MAPS rounds that built venues and parks since the 1990s.',
     src='City of Oklahoma City, MAPS 4',url='https://okc.gov/government/maps-4')),
 'crime':dict(pop=C[JI]['pop'],low=[[C[j]['n'],r4(D['raw']['crime'][j])] for j in low_us],
   ex=dict(city='Oakland',text='Oakland, California, restarted Operation Ceasefire in 2012. Police, community groups and service providers focus on the small number of people most likely to shoot or be shot, with a clear message, real help and swift consequences. An evaluation by Northeastern, Northwestern and Rutgers researchers credited it with a 32% drop in gun homicides.',
     src='ABC7 News, August 2018',url='https://abc7news.com/ceasefire-strategy-opd-oakland-police-department/4033914/')),
 'housing':dict(inc=r4(D['raw']['inc_pc'][JI]),
   ex=dict(city='Austin',text='Austin, one of the peers in JCC\'s municipal finance study, loosened zoning and parking rules for years: mixed-use zoning in 2007, easier backyard homes in 2015, and an end to parking minimums in 2023. It added about 120,000 homes from 2015 to 2024, up 30% while the US grew 9%. Median rent fell more than 16% from 2021 to 2026, a Pew analysis found.',
     src='Smart Cities Dive on Pew Charitable Trusts, March 2026',url='https://www.smartcitiesdive.com/news/austin-texas-housing-policy-reform-rent/815208/'))}
out=dict(w=D['weights'],pillars=D['pillars'],ind=[dict(k=i['key'],p=i['pillar'],w=i['w']) for i in D['indicators']],
 score={k:D['score'][k] for k in IND},
 cities=[dict(n=c['n'],c=c['c'],u4=int(U4[k]),us=int(bool(c['us'])),r=u4r.get(k,0),o=c['o'],xy=XY[c['code']]) for k,c in enumerate(C)],
 ji=JI,levers=levers,raw=raw,real=real,prog=PR)
s=json.dumps(out,separators=(',',':'),ensure_ascii=False); open('story_data.json','w').write(s)
print(len(s), C[JI]['n'], u4r[JI], [C[k]['n'] for k in idx[49:51]])
for L in levers: print(L['k'],L['ctrl'],round(L['jax'],3),'->',round(L['med'],3),L['tgtLab'],'rough' if L['rough'] else '')
print(real['crime']['low'], real['rec']['usmax'], real['rec']['usmaxv'])
