# Top50Connorometer: Path to the Top 50

A scrolling story page for Jacksonville CEOs, built by the Jacksonville Civic Council (JCC). It opens on a globe of the 845 cities in Oxford Economics' Global Cities Index with fewer than 4 million people. It then shows that Jacksonville ranks 97th in that group and ends with a calculator showing what it would take to reach the Top 50.

## Publishing and Oxford's permission

Oxford Economics gave JCC written permission (October 2026) to publish this page. The live site is GitHub Pages, served from the `docs/` folder on `main`:

https://mrronnoc32.github.io/Top50Connorometer/

- `docs/index.html` is the published page. It contains data derived from the Oxford index, which is covered by that permission.
- Oxford's raw files (`*.xlsx`, `*.gpkg`) and intermediate build data stay out of git. `.gitignore` blocks them.
- To update the site, run `./build.sh`, then commit and push `docs/index.html`.

## Build

You need Python 3 with `pandas`, `numpy`, `scipy` and `openpyxl`, plus Oxford's files in one folder:

- `Global Cities Index data.xlsx`
- `City reference.xlsx`
- `City reference.gpkg`

From the repo folder, run:

```sh
./build.sh "/path/to/JCC Global Cities Index data"
```

With no argument, the script looks one folder up. It writes `dist/index.html`, a single self-contained file, and copies it to `docs/index.html` for GitHub Pages.

## What's in here

| Path | What it does |
| --- | --- |
| `src/page.html` | The page: globe, "97th" section, calculator, method notes. The build fills in the data. |
| `scripts/load.py` | Reads Oxford's workbook. |
| `scripts/gen_v6.py` | Builds Oxford's 2026 scores and raw values, and fits the indicator weights inside each pillar. |
| `scripts/reg.py`, `scripts/model_params.py` | Fit a curve per metric from raw value to Oxford's 0 to 100 score. |
| `scripts/city_xy.py` | Takes metro center points from the boundaries file. |
| `scripts/story_data.py` | Assembles what the page needs: cities, all 27 levers with who-controls-it tags, the Top 50 typical values. |
| `scripts/progress_data.py` | Three editions of scores for Jacksonville and the 13 peers from JCC's municipal finance study. |
| `scripts/story_extras.py` | Under-4M ranks for each edition (each edition's own populations) and the five US and Canada cities to watch. |
| `scripts/assemble.py` | Writes `dist/index.html`. |
| `vendor/` | D3 7.8.5 (ISC license) and Natural Earth land outlines from world-atlas 2.0.2 (public domain). |

## How the calculator works

1. **Metric score.** A fitted power curve, rescaled 0 to 100, turns each raw value into Oxford's score. Fits have R² of 0.976 or higher for 25 of 27 metrics. Employment growth (0.92) and population growth (0.90) are rough.
2. **Pillar and overall.** Fitted weights inside each pillar, then Oxford's 30/25/25/10/10 pillar weights, with 0 to 100 rescaling at each step. This reproduces every city's published rank for 2024 to 2026.
3. **Anchoring.** Every other city keeps Oxford's actual 2026 scores. A lever changes only Jacksonville's score, by the amount the curve predicts. With nothing moved, the page shows Oxford's 97th exactly.

Checks on the built page, using the 2026 data:

- No changes: 97th.
- Recreation, crime and income equality halfway to the Top 50 typical value: about 65th.
- All three fully matched: about 44th.
- Demo scenario (the top five levers in the priorities chart, each closing half its gap): about 58th.
- Under-4M group: 850 (2024), 846 (2025), 845 (2026) cities; Jacksonville 103rd, 120th, 97th.

These agree with a second method (nearest-city lookup) to within 5 places.

**Flags**

- The curves are post-hoc. They were chosen after the pre-registered methods failed to reproduce Oxford's formula.
- Ranks are estimates.
- Governance (set nationally) and educational attainment and life expectancy (measured for Florida) aren't levers. They stay fixed at their 2026 values. So do natural disasters, economic stability and age profile.
- The "city to watch" line comes from news coverage of the 2026 index. Confirm it against Oxford's report before wider use.

## Contact

Connor Oswald, Director of Research, Jacksonville Civic Council.
