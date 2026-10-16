"""Three editions (2024-2026) of Oxford scores for Jacksonville and the 13 peers from JCC's
municipal finance study (7 core, 6 extended). Writes progress.json. Scores only."""
import json, math
import pandas as pd
from load import load, F, P
PEERS = [("Jacksonville","subject"),("San Antonio","core"),("Las Vegas","core"),("Virginia Beach","core"),("Tampa","core"),
         ("Orlando","core"),("Sacramento","core"),("Richmond","core"),("Charlotte","extended"),("Nashville","extended"),
         ("Tucson","extended"),("Memphis","extended"),("Raleigh","extended"),("Austin","extended")]
KEY = {"GDP size":"gdp_size","GDP growth":"gdp_growth","Economic stability":"econ_stab","GDP per person":"gdp_pc",
 "Employment growth":"emp_growth","Economic diversity":"econ_div","Population growth":"pop_growth","Age profile":"age",
 "Universities":"univ","Corporate HQs":"hq","Educational attainment":"edu","Foreign-born population":"foreign",
 "Income equality":"ineq","Income per person":"inc_pc","Housing expenditure":"housing","Life expectancy":"life",
 "Crime rate":"crime","Internet speed":"internet","Recreation & cultural sites":"rec","Air quality":"air",
 "Emissions intensity":"emis","Natural disasters":"disaster","Temperature anomalies":"temp","Rainfall anomalies":"rain",
 "Institutions":"inst","Political stability":"polstab","Business environment":"busenv","Civil liberties":"civlib"}
PK = dict(zip(P, ["econ","hc","qol","env","gov"]))
YEARS = [2024, 2025, 2026]
num = lambda v: None if v is None or (isinstance(v, float) and math.isnan(v)) else round(float(v), 2)
out = {"years": YEARS, "cities": [], "pillarsOf": {}}
data = {y: load(y) for y in YEARS}
for y in YEARS:
    s, r, raw, grp = data[y]
    for p, cols in grp.items():
        for c in cols: out["pillarsOf"][KEY[c]] = PK[p]
for name, tier in PEERS:
    rec = {"n": name, "tier": tier, "overall": [], "rank": [], "pil": {k: [] for k in PK.values()}, "pilRank": {k: [] for k in PK.values()}, "ind": {}}
    for yi, y in enumerate(YEARS):
        s, r, raw, grp = data[y]
        row = s[(s.City == name) & (s.Country == "United States")]; assert len(row) == 1, (name, y)
        row = row.iloc[0]; rr = r[(r.City == name) & (r.Country == "United States")].iloc[0]
        rec["overall"].append(num(row["Overall"])); rec["rank"].append(int(rr["Overall"]))
        for p, k in PK.items(): rec["pil"][k].append(num(row[p])); rec["pilRank"][k].append(int(rr[p]))
        for c in s.columns[9:]:
            k = KEY[c]; rec["ind"].setdefault(k, [None] * len(YEARS)); rec["ind"][k][yi] = num(row[c])
    out["cities"].append(rec)
m = pd.read_excel(F, sheet_name="Metadata")
m = m[(m.Indicator != "Natural disasters") | (m["Raw data unit"] == "Index")]
out["notes"] = {KEY[i]: str(n) for i, n in zip(m.Indicator, m.Notes) if i in KEY and isinstance(n, str)}
json.dump(out, open("progress.json", "w"), separators=(",", ":"))
j = out["cities"][0]; print("progress.json", j["rank"], j["ind"]["crime"], j["ind"]["internet"], j["ind"]["rec"]); print(out["notes"])
