# Small in Size. Big on Risk. — Australian Small Businesses

FIT3179 Data Visualisation 2 · Satvik Satvik (35411775) · Monash University · October 2026

Live page: https://satviktomar.github.io/dv2-australian-small-business/

## Repository layout
- `index.html` — the single scrollable page
- `specs/` — one human-readable Vega-Lite JSON specification per chart (12 charts, 3 map idioms)
- `data/` — tidy CSV/JSON files used by the charts, plus `aus_states.topojson` (map boundaries)
- `scripts/build_data.py` — rebuilds `data/` from the original ABS/ASIC workbooks
- `scripts/gen_specs.py` — regenerates the specs in `specs/`
- `css/`, `js/` — styling and the embedding script
- `sketch.pdf` — the A4 design sketch

## Data sources
1. Australian Bureau of Statistics — Counts of Australian Businesses, including Entries and Exits, Jul 2022–Jun 2026; National, State and Territory Population, Mar 2026.
2. Australian Securities & Investments Commission — Insolvency statistics Series 1 (12 Oct 2026) and Series 3.1 (2024–25).
