"""Level 1 anchored-regression parameters for the Jax Path to the Top 50 page (fit 15 Oct 2026, Oxford GCI 2026, all 1,000 cities).
For each indicator: score_hat(x) = 100 * (clip(dir * BoxCox(x - shift, lam), lo, hi) - a) / (b - a).
Page use: Jax new score = Oxford score + score_hat(new) - score_hat(old), clamped 0..100. POST-HOC (not pre-registered)."""
import json, numpy as np
exec(open('reg.py').read().split("def chain")[0].replace("print(","(lambda *a,**k:None)("))
LEVERS=['rec','crime','ineq','univ','emp_growth','housing','foreign','hq','emis','gdp_pc','gdp_size','econ_div']
out={}
for i in IND:
    x=np.array(D['raw'][i['key']],float); d=i['dir']; r=res[i['key']]; l=r['lam']; p=r['clip']
    sh=x.min()-1e-6*(x.max()-x.min()+1e-9); v=d*bc(x-sh,l); lo,hi=np.percentile(v,[p,100-p]); vv=np.clip(v,lo,hi)
    out[i['key']]=dict(name=i['name'],dir=d,lam=l,shift=float(sh),lo=float(lo),hi=float(hi),a=float(vv.min()),b=float(vv.max()),r2=float(r['r2']),rmse=float(r['rmse']),lever=i['key'] in LEVERS)
json.dump(dict(method=__doc__,indicators=out),open('model_params.json','w'),indent=1)
print(len(out),sum(o['lever'] for o in out.values()))
