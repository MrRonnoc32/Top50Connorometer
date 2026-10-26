"""Additions to story_data.json: under-4M ranks by edition (each edition's own populations),
the five US/Canada 'cities to watch' from Oxford's 2026 key findings page."""
import json, pandas as pd
from load import load
S = json.load(open("story_data.json")); D = json.load(open("conn_data.json"))
ref = pd.read_excel("City reference.xlsx").set_index("Code")
P = ["Economics", "Human capital", "Quality of life", "Environment", "Governance"]; PK = ["econ", "hc", "qol", "env", "gov"]
u4h = {"years": [2024, 2025, 2026], "n": [], "overall": [], "pil": {k: [] for k in PK}, "all": [], "allPil": {k: [] for k in PK}}
for y in u4h["years"]:
    s, r, raw, grp = load(y); s = s.set_index("Code"); r = r.set_index("Code")
    sub = s[ref[f"{y} index population"].reindex(s.index) < 4e6]
    rk = lambda col: int((sub[col] > sub.loc["USM37", col]).sum() + 1)
    u4h["n"].append(len(sub)); u4h["overall"].append(rk("Overall")); u4h["all"].append(int(r.loc["USM37", "Overall"]))
    for p, k in zip(P, PK): u4h["pil"][k].append(rk(p)); u4h["allPil"][k].append(int(r.loc["USM37", p]))
WATCH = [("San Antonio", "United States"), ("Boise", "United States"), ("Edmonton", "Canada"), ("Jacksonville", "United States"), ("Durham", "United States")]
codes = [c["code"] for c in D["cities"]]
watch = []
for n, c in WATCH:
    k = [i for i, x in enumerate(D["cities"]) if x["n"] == n and x["c"] == c]; assert len(k) == 1, n
    watch.append(k[0])
# Jacksonville's raw values by edition, in the page's display units (housing as %, GDP in US$ billions)
KEY = {"GDP size":"gdp_size","GDP growth":"gdp_growth","Economic stability":"econ_stab","GDP per person":"gdp_pc","Employment growth":"emp_growth",
 "Economic diversity":"econ_div","Population growth":"pop_growth","Age profile":"age","Universities":"univ","Corporate HQs":"hq",
 "Educational attainment":"edu","Foreign-born population":"foreign","Income equality":"ineq","Income per person":"inc_pc",
 "Housing expenditure":"housing","Life expectancy":"life","Crime rate":"crime","Recreation & cultural sites":"rec","Air quality":"air",
 "Emissions intensity":"emis","Natural disasters":"disaster","Temperature anomalies":"temp","Rainfall anomalies":"rain",
 "Institutions":"inst","Political stability":"polstab","Business environment":"busenv","Civil liberties":"civlib"}
SCALE = {"housing": 100, "gdp_size": 0.001}
jraw = {}
for yi, y in enumerate(u4h["years"]):
    s_, r_, raw, g_ = load(y); row = raw[raw.Code == "USM37"].iloc[0]
    for col, k in KEY.items():
        jraw.setdefault(k, [None, None, None])
        if col in raw.columns and pd.notna(row[col]): jraw[k][yi] = float(row[col]) * SCALE.get(k, 1)
S["u4h"] = u4h; S["watch"] = watch; S["jaxRaw"] = jraw
json.dump(S, open("story_data.json", "w"), separators=(",", ":"), ensure_ascii=False)
print(u4h); print([(S["cities"][k]["n"], S["cities"][k]["r"], S["cities"][k]["o"][2], S["cities"][k]["u4"]) for k in watch])
