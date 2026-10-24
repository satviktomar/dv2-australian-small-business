"""Builds the tidy CSV/JSON files in /data from the raw ABS and ASIC workbooks.
Run: python scripts/build_data.py <folder with raw xlsx>"""
import sys, json, csv, collections, openpyxl
RAW = sys.argv[1]; OUT = sys.argv[2]
def rows(book, sheet):
    wb = openpyxl.load_workbook(f"{RAW}/{book}", read_only=True, data_only=True)
    return [list(r) for r in wb[sheet].iter_rows(values_only=True)]
def write_csv(name, header, data):
    with open(f"{OUT}/{name}", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(data)
CABEE = "8165DC01_jun2026.xlsx"
YEARS = ["2022-23", "2023-24", "2024-25", "2025-26"]
SIZES = {"Non–employing": "Non-employing", "1–4": "1–4 employees", "5–19": "5–19 employees",
         "20–199": "20–199 employees", "200+": "200+ employees"}

# ---- Table 13: employment size flows ----
t13 = rows(CABEE, "Table 13"); yr = None; size_rows = []
for r in t13:
    if r[0] in YEARS: yr = r[0]; continue
    if yr and r[0] in SIZES:
        start, ent, ext, move, end = r[1], r[4], r[7], r[8], r[9]
        size_rows.append([yr, SIZES[r[0]], start, ent, ext, move, end])
write_csv("size_flows.csv", ["year", "size", "start", "entries", "exits", "net_movement", "end"], size_rows)

# waffle (June 2026 shares, largest remainder to 100 squares)
end26 = {s: e for y, s, *_, e in size_rows if y == "2025-26"}
groups = {"Non-employing": end26["Non-employing"], "1–4 employees": end26["1–4 employees"],
          "5–19 employees": end26["5–19 employees"],
          "20+ employees": end26["20–199 employees"] + end26["200+ employees"]}
tot = sum(groups.values()); exact = {k: 100 * v / tot for k, v in groups.items()}
sq = {k: int(v) for k, v in exact.items()}
for k in sorted(exact, key=lambda k: exact[k] - sq[k], reverse=True)[:100 - sum(sq.values())]: sq[k] += 1
waffle, i = [], 0
for k, n in sq.items():
    for _ in range(n):
        waffle.append({"id": i + 1, "col": i % 10, "row": i // 10, "size": k,
                       "share": round(exact[k], 1), "count": groups[k]}); i += 1
json.dump(waffle, open(f"{OUT}/waffle_size_2026.json", "w"), indent=1)

# slope: share of all businesses June 2022 vs June 2026
start22 = {s: st for y, s, st, *_ in size_rows if y == "2022-23"}
t22, t26 = sum(start22.values()), sum(end26.values())
write_csv("size_share_slope.csv", ["size", "year", "share", "count"],
          [[s, "June 2022", round(100 * start22[s] / t22, 1), start22[s]] for s in SIZES.values()] +
          [[s, "June 2026", round(100 * end26[s] / t26, 1), end26[s]] for s in SIZES.values()])

# waterfall: 1–4 employees, cumulative 2022-23 to 2025-26
g = [r for r in size_rows if r[1] == "1–4 employees"]
e, x, m = sum(r[3] for r in g), sum(r[4] for r in g), sum(r[5] for r in g)
s0, s1 = g[0][2], g[-1][6]
wf = [{"step": "June 2022", "start": 0, "end": s0, "value": s0, "kind": "Total"},
      {"step": "New entries", "start": s0, "end": s0 + e, "value": e, "kind": "Increase"},
      {"step": "Exits", "start": s0 + e, "end": s0 + e - x, "value": -x, "kind": "Decrease"},
      {"step": "Moved to another size", "start": s0 + e - x, "end": s0 + e - x + m, "value": m, "kind": "Decrease"},
      {"step": "June 2026", "start": 0, "end": s1, "value": s1, "kind": "Total"}]
assert s0 + e - x + m == s1
json.dump(wf, open(f"{OUT}/waterfall_1to4.json", "w"), indent=1)

# ---- Table 15 / 16 survival ----
surv = []
for r in rows(CABEE, "Table 15"):
    if r[0] in [k.replace("–", "-") if k.startswith("Non") else k for k in SIZES]:
        name = "Non-employing" if r[0].startswith("Non") else SIZES[r[0]]
        for yr_, rate in zip(["2023", "2024", "2025", "2026"], [r[3], r[5], r[7], r[9]]):
            surv.append([name, yr_, round(rate, 1)])
write_csv("survival_existing.csv", ["size", "survived_to_june", "rate"], surv)
ent = []
for r in rows(CABEE, "Table 16"):
    if r[0] in ["Non-employing", "1–4", "5–19", "20–199", "200+"]:
        name = "Non-employing" if r[0].startswith("Non") else SIZES[r[0]]
        ent.append([name, round(r[3], 1), round(r[7], 1)])
write_csv("survival_entrants.csv", ["size", "after_1_year", "after_3_years"], ent)

# ---- Table 4 states + Table 5 state survival + ERP ----
ABBR = {"New South Wales": "NSW", "Victoria": "VIC", "Queensland": "QLD", "South Australia": "SA",
        "Western Australia": "WA", "Tasmania": "TAS", "Northern Territory": "NT",
        "Australian Capital Territory": "ACT"}
yr = None; state = {}
for r in rows(CABEE, "Table 4"):
    if r[0] in YEARS: yr = r[0]; continue
    if yr == "2025-26" and r[0] in ABBR:
        state[r[0]] = {"businesses": r[9], "growth": round(r[11], 1), "entry_rate": round(r[12], 1),
                       "exit_rate": round(r[13], 1)}
for r in rows(CABEE, "Table 5"):
    if r[0] in ABBR: state[r[0]]["survival_4yr"] = round(r[9], 1)
erp = rows("abs_population_310104_mar2026.xlsx", "Data1")
hdr = erp[0]; last = [r for r in erp if r[0] is not None][-1]
print("ERP date:", last[0])
for j, h in enumerate(hdr):
    if h and "Persons" in str(h) and "Estimated Resident Population" in str(h):
        for n in ABBR:
            if f"{n} ;" in str(h) or f";  {n} ;" in str(h) or str(h).split(";")[1].strip() == n:
                state[n]["population"] = int(last[j])
# ---- ASIC Series 1 table 1.3 (FY2025-26 by state) ----
a13 = rows("asic_series1_2_oct2026.xlsx", "1.3"); fy = collections.defaultdict(lambda: [0] * 9); monthly = []
for r in a13[11:]:
    if r[4] is None or not isinstance(r[5], (int, float)): continue
    fy[r[1]] = [a + (b or 0) for a, b in zip(fy[r[1]], r[5:14])]
    monthly.append([r[1].replace("-20", "-"), int(r[2]), r[4], r[13]])
order = list(ABBR)
# label anchor (lon, lat) for the geographic maps and hexagon tile position (column, row)
GEO = {"NSW": (146.5, -32.3, 2.5, 1), "VIC": (144.3, -36.9, 2, 2), "QLD": (144.5, -22.5, 2, 0),
       "SA": (135.5, -30.0, 1.5, 1), "WA": (122.0, -26.0, 0.5, 1), "TAS": (146.6, -42.1, 2.5, 3),
       "NT": (133.4, -19.5, 1, 0), "ACT": (151.9, -36.2, 3, 2)}  # same column order as ASIC table
for n, v in zip(order, fy["2025-2026"][:8]): state[n]["insolvencies"] = v
st = []
for n, d in state.items():
    lon, lat, hc, hr = GEO[ABBR[n]]
    st.append([n, ABBR[n], lon, lat, hc, hr, d["businesses"], d["population"], round(1000 * d["businesses"] / d["population"], 1),
               d["growth"], d["entry_rate"], d["exit_rate"], d["survival_4yr"], d["insolvencies"],
               round(10000 * d["insolvencies"] / d["businesses"], 1)])
write_csv("states_2026.csv", ["state", "abbr", "label_lon", "label_lat", "hex_col", "hex_row", "businesses_jun2026", "population_mar2026", "businesses_per_1000",
                              "growth_pct_2025_26", "entry_rate", "exit_rate", "survival_jun22_jun26",
                              "insolvencies_fy2025_26", "insolvencies_per_10000"], st)
write_csv("insolvencies_monthly.csv", ["financial_year", "calendar_year", "month", "companies"], monthly)

# ---- Table 10 legal type rates ----
yr = None; lt = []
for r in rows(CABEE, "Table 10"):
    if r[0] in YEARS: yr = r[0]; continue
    if yr and r[0] in ["Total Companies", "Sole Proprietors", "Total Partnerships", "Trusts"]:
        lt.append([yr, r[0].replace("Total ", ""), round(r[11], 1), round(r[12], 1), r[8]])
write_csv("legal_type_rates.csv", ["year", "type", "entry_rate", "exit_rate", "end_count"], lt)

# ---- ASIC 3.1: industry, FTE size, causes; ABS Table 1 industry counts ----
A31 = "asic_series3_1_2024-25.xlsx"
ind_map = {"Accommodation and food services": "Accommodation and Food Services",
 "Administrative and support services": "Administrative and Support Services",
 "Labour hire": "Administrative and Support Services",
 "Agriculture, forestry and fishing": "Agriculture, Forestry and Fishing",
 "Arts and recreation services": "Arts and Recreation Services",
 "Construction (e.g. carpentry, plastering)": "Construction", "Education and training": "Education and Training",
 "Electricity, gas, water and waste services (e.g. electrical, plumbing)": "Electricity, Gas, Water and Waste Services",
 "Financial and insurances services": "Financial and Insurance Services",
 "Health care and social assistance": "Health Care and Social Assistance",
 "Information media and telecommunications": "Information Media and Telecommunications",
 "Manufacturing": "Manufacturing", "Mining": "Mining", "Other (business and personal) services": "Other Services",
 "Professional, scientific and technical services": "Professional, Scientific and Technical Services",
 "Public administration and safety": "Public Administration and Safety",
 "Rental, hiring and real estate services": "Rental, Hiring and Real Estate Services",
 "Retail trade": "Retail Trade", "Transport, postal and warehousing": "Transport, Postal and Warehousing",
 "Wholesale trade": "Wholesale Trade"}
ins = collections.Counter()
for r in rows(A31, "3.1.1"):
    if r[0] in ind_map: ins[ind_map[r[0]]] += r[9]
yr = None; abs_ind = {}
for r in rows(CABEE, "Table 1"):
    if r[0] in YEARS: yr = r[0]; continue
    if yr == "2024-25" and r[0] in ind_map.values(): abs_ind[r[0]] = r[8]
ti, ta = sum(ins.values()), sum(abs_ind.values())
SHORT = {"Accommodation and Food Services": "Hospitality (accommodation & food)",
 "Administrative and Support Services": "Admin & support (incl. labour hire)",
 "Agriculture, Forestry and Fishing": "Agriculture, forestry & fishing", "Arts and Recreation Services": "Arts & recreation",
 "Construction": "Construction", "Education and Training": "Education & training",
 "Electricity, Gas, Water and Waste Services": "Utilities", "Financial and Insurance Services": "Finance & insurance",
 "Health Care and Social Assistance": "Health care & social assistance",
 "Information Media and Telecommunications": "Media & telecommunications", "Manufacturing": "Manufacturing",
 "Mining": "Mining", "Other Services": "Other services (e.g. repairs, salons)",
 "Professional, Scientific and Technical Services": "Professional services",
 "Public Administration and Safety": "Public admin & safety",
 "Rental, Hiring and Real Estate Services": "Rental, hiring & real estate", "Retail Trade": "Retail trade",
 "Transport, Postal and Warehousing": "Transport & warehousing", "Wholesale Trade": "Wholesale trade"}
write_csv("industry_share.csv", ["industry", "measure", "share", "count"],
          [[SHORT[k], "Share of all businesses", round(100 * abs_ind[k] / ta, 1), abs_ind[k]] for k in abs_ind] +
          [[SHORT[k], "Share of company failures", round(100 * ins[k] / ti, 1), ins[k]] for k in abs_ind])
t = rows(A31, "3.1.2")
for r in t:
    if r[0] == "Total" and isinstance(r[1], (int, float)):
        fte = {"Fewer than 5 FTE": r[1], "5–19 FTE": r[2], "20–199 FTE": r[3], "200+ FTE": r[4], "Not known": r[5]}; break
json.dump(fte, open(f"{OUT}/asic_fte_2024_25.json", "w"), indent=1)
t = rows(A31, "3.1.3"); causes = t[5][1:15]; cz = []
for r in t[6:]:
    if r[0] in ind_map or r[0] == "Total":
        if r[0] == "Total" and cz and any(c[0] == "All industries" for c in cz): break
        reports = sum(ins_r[9] for ins_r in rows(A31, "3.1.1") if ins_r[0] == r[0]) if r[0] != "Total" else ti
        name = "All industries" if r[0] == "Total" else "Labour hire" if r[0] == "Labour hire" else "Admin & support (excl. labour hire)" if r[0].startswith("Administrative") else SHORT[ind_map[r[0]]]
        for c, v in zip(causes, r[1:15]):
            if c not in ("Other",): cz.append([name, c, v, reports, round(100 * v / reports, 1)])
write_csv("failure_causes.csv", ["industry", "cause", "reports_nominating", "reports_total", "pct_of_reports"], cz)
print(json.dumps(fte)); print(state["Western Australia"])
