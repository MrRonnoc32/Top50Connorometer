"""Build Connorometer v6 data JSON from Oxford's licensed GCI data (2024-2026).
v6 adds: GDP per person and US flag per city (for 'similar cities' and 'US only' peer modes),
and Jacksonville's Oxford pillar ranks by year (for guess-first mode)."""
import json
from load import *
ref = pd.read_excel("City reference.xlsx").set_index("Code")
meta = pd.read_excel(F, sheet_name="Metadata")
D = {y: load(y) for y in [2024, 2025, 2026]}
s26, r26, raw26, g26 = D[2026]
codes = list(s26.Code)
def by_code(df, col): return df.set_index("Code").loc[codes, col].astype(float).values
PK = {"Economics": "econ", "Human capital": "hc", "Quality of life": "qol", "Environment": "env", "Governance": "gov"}
DISP = {
 "GDP size": ("gdp_size", "US$ billions", 0.001, 1), "GDP growth": ("gdp_growth", "% per year, 5-yr forecast", 1, 2),
 "Economic stability": ("econ_stab", "std. dev. of yearly growth", 1, 2), "GDP per person": ("gdp_pc", "US$ thousands", 1, 1),
 "Employment growth": ("emp_growth", "% per year, 5-yr forecast", 1, 2), "Economic diversity": ("econ_div", "concentration index", 1, 3),
 "Population growth": ("pop_growth", "% per year", 1, 2), "Age profile": ("age", "old-age ratio, %", 1, 1),
 "Universities": ("univ", "ranking-weighted index", 1, 1), "Corporate HQs": ("hq", "firms", 1, 0),
 "Educational attainment": ("edu", "index, 0 to 1", 1, 3), "Foreign-born population": ("foreign", "% of residents", 1, 1),
 "Income equality": ("ineq", "ratio (Gini-type)", 1, 3), "Income per person": ("inc_pc", "PPP$ thousands", 1, 1),
 "Housing expenditure": ("housing", "% of income", 100, 1), "Life expectancy": ("life", "index, 0 to 1", 1, 3),
 "Crime rate": ("crime", "rate per 100,000", 1, 1), "Recreation & cultural sites": ("rec", "index", 1, 3),
 "Air quality": ("air", "µg/m³ PM2.5", 1, 1), "Emissions intensity": ("emis", "emissions to GDP ratio", 1, 1),
 "Natural disasters": ("disaster", "hazard index", 1, 1), "Temperature anomalies": ("temp", "°C, 10-yr average", 1, 2),
 "Rainfall anomalies": ("rain", "index (SPI)", 1, 2), "Institutions": ("inst", "index", 1, 1),
 "Political stability": ("polstab", "index", 1, 1), "Business environment": ("busenv", "index", 1, 2),
 "Civil liberties": ("civlib", "index", 1, 0)}
from scipy.optimize import nnls
inds, rawd, scd, jhist, sdchg = [], {}, {}, {}, {}
for pname in P:
    li = g26[pname]
    X = s26[li].values; t = s26[pname].values
    A = np.c_[X, np.ones(len(t)), -np.ones(len(t))]; w, _ = nnls(A, t); w = w[:-2] / w[:-2].sum()
    for c, wi in zip(li, w):
        key, unit, sc, dp = DISP[c]
        m = meta[meta.Indicator == c]
        if c == "Natural disasters": m = m[m["Raw data unit"] == "Index"]
        m = m.iloc[0]
        x = by_code(raw26, c); y = by_code(s26, c)
        d = 1 if np.corrcoef(x, y)[0, 1] > 0 else -1
        inds.append(dict(key=key, pillar=PK[pname], name=c, measures=m.Description, unit=unit, dp=dp, dir=d,
                         level=m["Geographic level"], w=round(float(wi), 4),
                         note=(m.Notes if isinstance(m.Notes, str) else "")))
        rawd[key] = [float(f"{v*sc:.6g}") for v in x]
        scd[key] = [round(float(v), 3) for v in y]
        hist = []
        for yy in [2024, 2025]:
            rw = D[yy][2]
            hist.append(float(f"{rw.set_index('Code').at['USM37', c]*sc:.6g}") if c in rw.columns else None)
        jhist[key] = hist
        r25 = D[2025][2]
        sdchg[key] = float(f"{np.std(by_code(r25, c)*sc - x*sc):.4g}") if c in r25.columns else 0.0
pil = {}
for yy in [2024, 2026]:
    s = D[yy][0]
    pil[str(yy)] = {PK[p]: [round(float(v), 3) for v in by_code(s, p)] for p in P}
gdppc = by_code(raw26, "GDP per person")
cities = []
for k, c in enumerate(codes):
    row = s26.iloc[k]
    cities.append(dict(n=row.City, c=row.Country, code=c, pop=int(ref.at[c, "2026 index population"]),
                       g=round(float(gdppc[k]), 2), us=1 if row.Country == "United States" else 0,
                       o=[int(D[y][1].set_index("Code").at[c, "Overall"]) for y in [2024, 2025, 2026]]))
jaxPR = {}
for y in [2024, 2025, 2026]:
    rr = D[y][1].set_index("Code").loc["USM37"]
    jaxPR[str(y)] = dict(overall=int(rr["Overall"]), **{PK[p]: int(rr[p]) for p in P})
out = dict(weights={"econ": .3, "hc": .25, "qol": .25, "env": .1, "gov": .1}, pillars=["econ", "hc", "qol", "env", "gov"],
           indicators=inds, cities=cities, raw=rawd, score=scd, jaxHist=jhist, sdChange=sdchg, pil=pil, jaxPR=jaxPR,
           oxfordOverall26=[round(float(v), 3) for v in by_code(s26, "Overall")])
js = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
open("conn_data.json", "w").write(js)
print("bytes", len(js.encode()), "inds", len(inds), "jaxPR", jaxPR)
