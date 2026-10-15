import pandas as pd, numpy as np
F="Global Cities Index data.xlsx"
P=["Economics","Human capital","Quality of life","Environment","Governance"]
def load(y):
    s=pd.read_excel(F,sheet_name=f"{y} scores",header=1)
    r=pd.read_excel(F,sheet_name=f"{y} ranks",header=1)
    raw=pd.read_excel(F,sheet_name=f"{y} raw data",header=1)
    hdr=pd.read_excel(F,sheet_name=f"{y} scores",header=None,nrows=1).iloc[0].ffill()
    grp={}
    for i,c in enumerate(s.columns[9:],start=9):
        grp.setdefault(hdr[i].replace(" category","").strip(),[]).append(c)
    grp={p:grp[g] for p,g in zip(P,grp)}
    return s,r,raw,grp
