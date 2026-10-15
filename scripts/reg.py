import json, numpy as np
from scipy.stats import spearmanr
D=json.load(open('conn_data.json')); C=D['cities']; N=len(C)
JI=[k for k,c in enumerate(C) if c['code']=='USM37'][0]
U4=np.array([c['pop']<4e6 for c in C])
IND=D['indicators']; P=D['pillars']; W=D['weights']
mm=lambda a:(a-a.min())/(a.max()-a.min())*100
def bc(x,l): return np.log(x) if abs(l)<1e-9 else (x**l-1)/l
res={}; pred={}
for i in IND:
    x=np.array(D['raw'][i['key']],float); y=np.array(D['score'][i['key']],float); d=i['dir']
    x0=x-x.min()+1e-6*(x.max()-x.min()+1e-9)
    best=None
    for l in np.linspace(-2,2,81):
        v=d*bc(x0,l)
        for p in [0,0.5,1,2.5,5]:
            lo,hi=np.percentile(v,[p,100-p]); f=mm(np.clip(v,lo,hi))
            e=f-y; rmse=np.sqrt((e**2).mean())
            if best is None or rmse<best[0]: best=(rmse,l,p,f)
    rmse,l,p,f=best; r2=1-((f-y)**2).sum()/((y-y.mean())**2).sum()
    res[i['key']]=dict(name=i['name'],pillar=i['pillar'],level=i['level'],rmse=round(rmse,2),maxerr=round(float(np.abs(f-y).max()),1),r2=round(r2,4),lam=round(l,2),clip=p,jax_obs=y[JI],jax_hat=round(f[JI],2))
    pred[i['key']]=f
def chain(S):
    tot=np.zeros(N)
    for p in P:
        acc=np.zeros(N)
        for i in IND:
            if i['pillar']==p: acc+=S[i['key']]*i['w']
        tot+=mm(acc)*W[p]
    return mm(tot)
def rk(t,mask=None):
    m=np.ones(N,bool) if mask is None else mask
    return int((t[m]>t[JI]+1e-9).sum()+1)
obs={i['key']:np.array(D['score'][i['key']]) for i in IND}
To=chain(obs); Tp=chain(pred)
def ranks(t,mask):
    idx=np.where(mask)[0]; o=idx[np.argsort(-t[idx])]; r=np.full(N,-1); r[o]=np.arange(1,len(o)+1); return r
ro=ranks(To,U4); rp=ranks(Tp,U4)
print('Level2 check (Oxford scores): Jax global',rk(To),'u4',rk(To,U4))
print('Regression chain: Jax global',rk(Tp),'u4',rk(Tp,U4))
print('Spearman overall (all 1000):',round(spearmanr(To,Tp)[0],4))
dd=np.abs(ro[U4]-rp[U4]); print('u4 rank diff median',np.median(dd),'p90',np.percentile(dd,90),'max',dd.max(),'within5',(dd<=5).mean().round(3))
top_o=set(np.where((ro>0)&(ro<=50))[0]); top_p=set(np.where((rp>0)&(rp<=50))[0]); print('Top50 overlap',len(top_o&top_p))
print()
for k,v in sorted(res.items(),key=lambda kv:kv[1]['rmse']): print(k,v)
json.dump(res,open('reg_results.json','w'),indent=1,default=float)
