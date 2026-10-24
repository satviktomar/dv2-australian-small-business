"""Writes one human-readable Vega-Lite JSON spec per chart into /specs."""
import json, os
OUT = os.path.join(os.path.dirname(__file__), "..", "specs")
S = "https://vega.github.io/schema/vega-lite/v5.json"
INK, TEAL, TERRA, SAND, GREY = "#1d3540", "#1f6f78", "#c0532b", "#efe6d6", "#b7c2c4"
SIZE4 = ["Non-employing", "1–4 employees", "5–19 employees", "20+ employees"]
RAMP4 = ["#12434a", "#2f8189", "#86bcb9", "#d6e6e1"]
PROJ = {"type": "conicEqualArea", "parallels": [-18, -36], "rotate": [-132.5, 0]}
TOPO = {"url": "data/aus_states.topojson", "format": {"type": "topojson", "feature": "states"}}
STATES = {"url": "data/states_2026.csv", "format": {"type": "csv", "parse": {
    "label_lon": "number", "label_lat": "number", "hex_col": "number", "hex_row": "number",
    "businesses_jun2026": "number", "population_mar2026": "number", "businesses_per_1000": "number",
    "growth_pct_2025_26": "number", "survival_jun22_jun26": "number", "insolvencies_fy2025_26": "number",
    "insolvencies_per_10000": "number", "entry_rate": "number", "exit_rate": "number"}}}
STATE_TT = [{"field": "state", "title": "State/territory"},
            {"field": "businesses_jun2026", "title": "Businesses (June 2026)", "format": ","},
            {"field": "businesses_per_1000", "title": "Businesses per 1,000 residents", "format": ".1f"},
            {"field": "growth_pct_2025_26", "title": "Growth 2025–26 (%)", "format": ".1f"},
            {"field": "insolvencies_fy2025_26", "title": "Companies entering insolvency 2025–26", "format": ","},
            {"field": "insolvencies_per_10000", "title": "Per 10,000 businesses", "format": ".1f"}]
specs = {}

specs["01_waffle_size"] = {
  "$schema": S, "description": "Waffle chart: 100 squares = all Australian businesses, June 2026, by employment size.",
  "data": {"url": "data/waffle_size_2026.json"}, "width": 300, "height": 300,
  "mark": {"type": "rect", "cornerRadius": 2},
  "encoding": {
    "x": {"field": "col", "type": "ordinal", "axis": None, "scale": {"paddingInner": 0.1}},
    "y": {"field": "row", "type": "ordinal", "axis": None, "scale": {"paddingInner": 0.1}},
    "color": {"field": "size", "type": "ordinal", "title": "Employment size",
              "scale": {"domain": SIZE4, "range": RAMP4},
              "legend": {"orient": "right", "labelFontSize": 14, "symbolType": "square", "symbolSize": 220}},
    "tooltip": [{"field": "size", "title": "Employment size"}, {"field": "share", "title": "Share of businesses (%)"},
                {"field": "count", "title": "Businesses", "format": ","}]}}

specs["02_slope_share"] = {
  "$schema": S, "description": "Slope chart: share of businesses by employment size, June 2022 vs June 2026.",
  "data": {"url": "data/size_share_slope.csv", "format": {"type": "csv", "parse": {"count": "number"}}},
  "transform": [
    {"calculate": "indexof(['20–199 employees','200+ employees'], datum.size) >= 0 ? '20+ employees' : datum.size", "as": "group"},
    {"aggregate": [{"op": "sum", "field": "count", "as": "count"}], "groupby": ["group", "year"]},
    {"joinaggregate": [{"op": "sum", "field": "count", "as": "total"}], "groupby": ["year"]},
    {"calculate": "100 * datum.count / datum.total", "as": "share"},
    {"calculate": "datum.group === 'Non-employing' || datum.group === '1–4 employees' ? datum.group : 'other'", "as": "focus"}],
  "width": "container", "height": 360,
  "encoding": {
    "x": {"field": "year", "type": "ordinal", "title": None, "scale": {"padding": 0.9},
          "axis": {"orient": "top", "domain": False, "ticks": False, "labelFontSize": 15, "labelFontWeight": 600, "labelAngle": 0}},
    "y": {"field": "share", "type": "quantitative", "title": "Share of all businesses (%)",
          "scale": {"domain": [0, 70]}, "axis": {"grid": True, "tickCount": 7}},
    "color": {"field": "focus", "type": "nominal", "legend": None,
              "scale": {"domain": ["Non-employing", "1–4 employees", "other"], "range": [TEAL, TERRA, "#9aa6a8"]}},
    "detail": {"field": "group"},
    "tooltip": [{"field": "group", "title": "Employment size"}, {"field": "year", "title": "Date"},
                {"field": "share", "title": "Share (%)", "format": ".1f"}, {"field": "count", "title": "Businesses", "format": ","}]},
  "layer": [
    {"mark": {"type": "line", "strokeWidth": 3}},
    {"mark": {"type": "circle", "size": 90, "opacity": 1}},
    {"transform": [{"filter": "datum.year === 'June 2022'"}],
     "mark": {"type": "text", "align": "right", "dx": -12, "fontSize": 14},
     "encoding": {"text": {"field": "share", "format": ".1f"}}},
    {"transform": [{"filter": "datum.year === 'June 2026'"},
                   {"calculate": "format(datum.share, '.1f') + '%  ' + datum.group", "as": "lab"}],
     "mark": {"type": "text", "align": "left", "dx": 12, "fontSize": 14, "fontWeight": 600},
     "encoding": {"text": {"field": "lab"}}}]}

specs["03_waterfall_1to4"] = {
  "$schema": S, "description": "Waterfall: how the 1–4 employee group changed between June 2022 and June 2026.",
  "data": {"url": "data/waterfall_1to4.json"}, "width": "container", "height": 340,
  "transform": [{"calculate": "datum.kind === 'Total' ? format(datum.value, ',') : (datum.value > 0 ? '+' : '−') + format(abs(datum.value), ',')", "as": "label"},
                {"calculate": "max(datum.start, datum.end)", "as": "top"},
                {"window": [{"op": "lead", "field": "step", "as": "next"}]}],
  "encoding": {"x": {"field": "step", "type": "ordinal", "sort": None, "title": None,
                     "axis": {"labelAngle": 0, "labelFontSize": 14, "labelLimit": 160, "domain": False, "ticks": False}}},
  "layer": [
    {"mark": {"type": "bar", "width": {"band": 0.62}},
     "encoding": {"y": {"field": "start", "type": "quantitative", "title": "Businesses with 1–4 employees",
                        "scale": {"domain": [0, 1200000]}, "axis": {"format": "~s", "tickCount": 6}},
                  "y2": {"field": "end"},
                  "color": {"field": "kind", "type": "nominal", "title": None,
                            "scale": {"domain": ["Total", "Increase", "Decrease"], "range": [INK, TEAL, TERRA]},
                            "legend": {"orient": "top-right", "direction": "horizontal"}},
                  "tooltip": [{"field": "step", "title": "Step"}, {"field": "label", "title": "Businesses"}]}},
    {"mark": {"type": "rule", "strokeDash": [4, 3], "color": "#7b8b8e", "xOffset": 52, "x2Offset": -52},
     "transform": [{"filter": "datum.next != null"}],
     "encoding": {"y": {"field": "end", "type": "quantitative"}, "x2": {"field": "next"}}},
    {"mark": {"type": "text", "dy": -10, "fontSize": 15, "fontWeight": 600, "color": INK},
     "encoding": {"y": {"field": "top", "type": "quantitative"}, "text": {"field": "label"}}}]}

specs["04_map_choropleth_density"] = {
  "$schema": S, "description": "Choropleth: businesses per 1,000 residents by state/territory (ABS CABEE June 2026 ÷ ABS ERP March 2026).",
  "width": "container", "height": 430, "projection": PROJ,
  "layer": [
    {"data": TOPO,
     "params": [{"name": "hover", "select": {"type": "point", "on": "pointerover", "clear": "pointerout", "fields": ["properties.name"]}}],
     "transform": [{"lookup": "properties.name", "from": {"data": STATES, "key": "state",
                    "fields": ["state", "businesses_jun2026", "businesses_per_1000", "growth_pct_2025_26", "insolvencies_fy2025_26", "insolvencies_per_10000"]}}],
     "mark": {"type": "geoshape", "stroke": "#faf7f2"},
     "encoding": {
       "color": {"field": "businesses_per_1000", "type": "quantitative", "title": "Businesses per 1,000 residents",
                 "scale": {"type": "threshold", "domain": [70, 85, 100], "range": ["#efe3cc", "#a9cfc6", "#4f9a9b", "#12434a"]},
                 "legend": {"orient": "bottom", "direction": "horizontal", "symbolType": "square", "symbolSize": 200}},
       "strokeWidth": {"condition": {"param": "hover", "empty": False, "value": 3}, "value": 1},
       "tooltip": STATE_TT}},
    {"data": STATES, "mark": {"type": "text", "fontSize": 13, "fontWeight": 700, "lineHeight": 15},
     "transform": [{"calculate": "[datum.abbr, format(datum.businesses_per_1000, '.0f')]", "as": "lab"}],
     "encoding": {"longitude": {"field": "label_lon", "type": "quantitative"},
                  "latitude": {"field": "label_lat", "type": "quantitative"},
                  "text": {"field": "lab"},
                  "color": {"condition": {"test": "datum.businesses_per_1000 >= 100", "value": "#ffffff"}, "value": INK}}}]}

specs["05_map_symbols_insolvency"] = {
  "$schema": S, "description": "Proportional symbol map: companies entering external administration for the first time, FY2025–26 (ASIC Series 1).",
  "width": "container", "height": 430, "projection": PROJ,
  "layer": [
    {"data": TOPO, "mark": {"type": "geoshape", "fill": "#e9e2d4", "stroke": "#faf7f2", "strokeWidth": 1.5}},
    {"data": STATES, "mark": {"type": "circle", "color": TERRA, "opacity": 0.78, "stroke": "#ffffff", "strokeWidth": 1.5},
     "encoding": {"longitude": {"field": "label_lon", "type": "quantitative"},
                  "latitude": {"field": "label_lat", "type": "quantitative"},
                  "size": {"field": "insolvencies_fy2025_26", "type": "quantitative",
                           "title": "Companies entering insolvency, 2025–26",
                           "scale": {"type": "linear", "zero": True, "domain": [0, 5500], "range": [0, 4000]},
                           "legend": {"orient": "bottom", "direction": "horizontal", "values": [500, 2000, 5000], "symbolFillColor": TERRA, "symbolStrokeColor": "#fff"}},
                  "tooltip": STATE_TT}},
    {"data": STATES,
     "transform": [{"calculate": "datum.abbr + ' ' + format(datum.insolvencies_fy2025_26, ',')", "as": "lab"},
                   {"calculate": "datum.abbr === 'ACT' ? datum.label_lat - 1.6 : datum.abbr === 'TAS' ? datum.label_lat - 2.2 : datum.insolvencies_fy2025_26 > 2000 ? datum.label_lat : datum.label_lat + 1.9", "as": "lab_lat"}],
     "mark": {"type": "text", "fontSize": 13, "fontWeight": 700},
     "encoding": {"longitude": {"field": "label_lon", "type": "quantitative"},
                  "latitude": {"field": "lab_lat", "type": "quantitative"}, "text": {"field": "lab"},
                  "color": {"condition": {"test": "datum.insolvencies_fy2025_26 > 2000", "value": "#ffffff"}, "value": INK}}}]}

HEX = "M0,-1L0.866,-0.5L0.866,0.5L0,1L-0.866,0.5L-0.866,-0.5Z"
specs["06_map_hex_rate"] = {
  "$schema": S, "description": "Hexagon tile map (equal-area bin map): companies entering insolvency per 10,000 businesses, FY2025–26. Every state gets the same-sized tile, so small territories are not hidden.",
  "data": STATES, "width": 340, "height": 322,
  "transform": [{"calculate": "datum.hex_row * 0.866", "as": "hy"},
                {"calculate": "[datum.abbr, format(datum.insolvencies_per_10000, '.0f')]", "as": "lab"}],
  "encoding": {"x": {"field": "hex_col", "type": "quantitative", "axis": None, "scale": {"domain": [-0.15, 3.75]}},
               "y": {"field": "hy", "type": "quantitative", "axis": None, "scale": {"domain": [3.15, -0.55]}}},
  "layer": [
    {"mark": {"type": "point", "shape": HEX, "filled": True, "size": 9000, "stroke": "#faf7f2", "strokeWidth": 3, "opacity": 1},
     "encoding": {"color": {"field": "insolvencies_per_10000", "type": "quantitative",
                            "title": "Per 10,000 businesses",
                            "scale": {"domain": [25, 70], "range": ["#f3e3cf", "#8f2f12"]},
                            "legend": {"orient": "right", "gradientLength": 200}},
                  "tooltip": STATE_TT}},
    {"mark": {"type": "text", "fontSize": 14, "fontWeight": 700, "lineHeight": 16},
     "encoding": {"text": {"field": "lab"},
                  "color": {"condition": {"test": "datum.insolvencies_per_10000 > 48", "value": "#ffffff"}, "value": INK}}}]}

SIZE5 = ["Non-employing", "1–4 employees", "5–19 employees", "20–199 employees", "200+ employees"]
specs["07_heatmap_survival"] = {
  "$schema": S, "description": "Cohort survival heatmap: % of businesses operating in June 2022 still operating each June, by starting employment size.",
  "data": {"url": "data/survival_existing.csv", "format": {"type": "csv", "parse": {"rate": "number"}}},
  "width": "container", "height": 300,
  "encoding": {"x": {"field": "survived_to_june", "type": "ordinal", "title": "Still trading in June…",
                     "axis": {"orient": "top", "labelAngle": 0, "domain": False, "ticks": False}},
               "y": {"field": "size", "type": "ordinal", "sort": SIZE5, "title": None,
                     "axis": {"domain": False, "ticks": False, "labelFontSize": 14}},
               "tooltip": [{"field": "size", "title": "Size in June 2022"}, {"field": "survived_to_june", "title": "Still trading in June"},
                           {"field": "rate", "title": "Survival (%)", "format": ".1f"}]},
  "layer": [
    {"mark": {"type": "rect", "stroke": "#faf7f2", "strokeWidth": 3},
     "encoding": {"color": {"field": "rate", "type": "quantitative", "title": "Still trading (%)",
                            "scale": {"domain": [50, 100], "range": ["#f3e3cf", "#12434a"]},
                            "legend": {"orient": "bottom", "direction": "horizontal", "gradientLength": 260}}}},
    {"mark": {"type": "text", "fontSize": 15, "fontWeight": 600},
     "encoding": {"text": {"field": "rate", "format": ".1f"},
                  "color": {"condition": {"test": "datum.rate > 75", "value": "#ffffff"}, "value": INK}}}]}

specs["08_dumbbell_entrants"] = {
  "$schema": S, "description": "Dumbbell chart: survival of businesses that started in 2022–23 after one year vs after three years.",
  "data": {"url": "data/survival_entrants.csv", "format": {"type": "csv", "parse": {"after_1_year": "number", "after_3_years": "number"}}},
  "width": "container", "height": 280,
  "encoding": {"y": {"field": "size", "type": "ordinal", "sort": SIZE5, "title": "Size when started",
                     "axis": {"domain": False, "ticks": False, "labelFontSize": 14, "titlePadding": 12}}},
  "layer": [
    {"mark": {"type": "rule", "strokeWidth": 4, "color": "#c9d2d3"},
     "encoding": {"x": {"field": "after_3_years", "type": "quantitative", "title": "Still trading (%)", "scale": {"domain": [0, 100]}},
                  "x2": {"field": "after_1_year"}}},
    {"transform": [{"fold": ["after_1_year", "after_3_years"], "as": ["when", "rate"]},
                   {"calculate": "datum.when === 'after_1_year' ? 'After 1 year (June 2024)' : 'After 3 years (June 2026)'", "as": "When"}],
     "layer": [
       {"mark": {"type": "circle", "size": 220, "opacity": 1},
        "encoding": {"x": {"field": "rate", "type": "quantitative"},
                     "color": {"field": "When", "type": "nominal", "title": None, "scale": {"range": [TEAL, TERRA]},
                               "legend": {"orient": "top", "direction": "horizontal"}},
                     "tooltip": [{"field": "size", "title": "Size when started"}, {"field": "When"}, {"field": "rate", "title": "Still trading (%)", "format": ".1f"}]}},
       {"mark": {"type": "text", "dy": -16, "fontSize": 13, "fontWeight": 600},
        "encoding": {"x": {"field": "rate", "type": "quantitative"}, "text": {"field": "rate", "format": ".0f"},
                     "color": {"field": "When", "type": "nominal", "legend": None}}}]}]}

LT = ["Sole Proprietors", "Companies", "Trusts", "Partnerships"]
specs["09_connected_scatter_legal"] = {
  "$schema": S, "description": "Connected scatterplot: entry rate vs exit rate for each legal structure, 2022–23 to 2025–26.",
  "data": {"url": "data/legal_type_rates.csv", "format": {"type": "csv", "parse": {"entry_rate": "number", "exit_rate": "number", "end_count": "number"}}},
  "width": "container", "height": 420,
  "encoding": {"x": {"field": "entry_rate", "type": "quantitative", "title": "Entry rate (% of businesses that started this year)", "scale": {"domain": [5, 25]}},
               "y": {"field": "exit_rate", "type": "quantitative", "title": "Exit rate (% that closed this year)", "scale": {"domain": [5, 25]}}},
  "layer": [
    {"data": {"values": [{"x": 5, "y": 5}, {"x": 25, "y": 25}]}, "mark": {"type": "line", "strokeDash": [5, 4], "color": "#8a9a9c"},
     "encoding": {"x": {"field": "x", "type": "quantitative"}, "y": {"field": "y", "type": "quantitative"}}},
    {"data": {"values": [{"x": 5.6, "y": 24, "t": "↖ More closures than starts: shrinking"},
                         {"x": 15.5, "y": 6, "t": "More starts than closures: growing ↘"}]},
     "mark": {"type": "text", "align": "left", "fontSize": 13, "fontStyle": "italic", "color": "#5d6f72"},
     "encoding": {"x": {"field": "x", "type": "quantitative"}, "y": {"field": "y", "type": "quantitative"}, "text": {"field": "t"}}},
    {"params": [{"name": "pick", "select": {"type": "point", "fields": ["type"]}, "bind": "legend"}],
     "mark": {"type": "line", "strokeWidth": 2.5, "point": {"filled": True, "size": 70}},
     "encoding": {"order": {"field": "year"},
                  "color": {"field": "type", "type": "nominal", "title": "Legal structure (click to focus)", "sort": LT,
                            "scale": {"domain": LT, "range": [TERRA, TEAL, "#c8922a", "#6c6f93"]},
                            "legend": {"orient": "bottom", "direction": "horizontal"}},
                  "opacity": {"condition": {"param": "pick", "value": 1}, "value": 0.15},
                  "tooltip": [{"field": "type", "title": "Structure"}, {"field": "year", "title": "Year"},
                              {"field": "entry_rate", "title": "Entry rate (%)"}, {"field": "exit_rate", "title": "Exit rate (%)"},
                              {"field": "end_count", "title": "Businesses at year end", "format": ","}]}},
    {"data": {"values": [{"type": "Sole Proprietors", "x": 19.6, "y": 22.4, "lab": "Sole traders"},
                         {"type": "Companies", "x": 17.6, "y": 13.0, "lab": "Companies"},
                         {"type": "Trusts", "x": 11.1, "y": 8.6, "lab": "Trusts"},
                         {"type": "Partnerships", "x": 5.6, "y": 13.0, "lab": "Partnerships"}]},
     "mark": {"type": "text", "align": "left", "fontSize": 14, "fontWeight": 700},
     "encoding": {"x": {"field": "x", "type": "quantitative"}, "y": {"field": "y", "type": "quantitative"},
                  "text": {"field": "lab"}, "color": {"field": "type", "type": "nominal", "legend": None},
                  "opacity": {"condition": {"param": "pick", "value": 1}, "value": 0.15}}}]}

ind_data = {"url": "data/industry_share.csv", "format": {"type": "csv", "parse": {"share": "number", "count": "number"}}}
ind_tf = [{"pivot": "measure", "value": "share", "groupby": ["industry"]},
          {"calculate": "datum['Share of company failures'] - datum['Share of all businesses']", "as": "gap"}]
ysort = {"field": "Share of company failures", "order": "descending"}
ytt = [{"field": "industry", "title": "Industry"}, {"field": "Share of all businesses", "title": "Share of all businesses (%)"},
       {"field": "Share of company failures", "title": "Share of company failures (%)"}]
specs["10_butterfly_industry"] = {
  "$schema": S, "description": "Butterfly chart: each industry's share of all businesses (ABS, June 2025) vs its share of company failures reported to ASIC (2024–25).",
  "data": ind_data, "transform": ind_tf, "spacing": 0,
  "hconcat": [
    {"width": 230, "height": 470, "title": {"text": "Share of all businesses (%)", "fontSize": 14, "color": TEAL, "anchor": "end"},
     "mark": {"type": "bar", "color": TEAL, "height": {"band": 0.72}},
     "encoding": {"y": {"field": "industry", "type": "nominal", "sort": ysort, "axis": None},
                  "x": {"field": "Share of all businesses", "type": "quantitative", "title": None,
                        "scale": {"reverse": True, "domain": [0, 26]}, "axis": {"tickCount": 5, "grid": False}},
                  "tooltip": ytt}},
    {"width": 250, "height": 470, "view": {"stroke": None},
     "encoding": {"y": {"field": "industry", "type": "nominal", "sort": ysort, "axis": None},
                  "text": {"field": "industry"}},
     "layer": [{"transform": [{"filter": "datum.gap > 1"}], "mark": {"type": "text", "align": "center", "fontSize": 13, "fontWeight": 700}},
               {"transform": [{"filter": "datum.gap <= 1"}], "mark": {"type": "text", "align": "center", "fontSize": 13, "color": "#566a70"}}]},
    {"width": 230, "height": 470, "title": {"text": "Share of company failures (%)", "fontSize": 14, "color": TERRA, "anchor": "start"},
     "mark": {"type": "bar", "height": {"band": 0.72}},
     "encoding": {"y": {"field": "industry", "type": "nominal", "sort": ysort, "axis": None},
                  "x": {"field": "Share of company failures", "type": "quantitative", "title": None,
                        "scale": {"domain": [0, 26]}, "axis": {"tickCount": 5, "grid": False}},
                  "color": {"condition": {"test": "datum.gap > 1", "value": TERRA}, "value": "#d9b8a9"},
                  "tooltip": ytt}}]}

TOP = ["Inadequate cash flow or high cash use", "Poor strategic management of business", "Trading losses",
       "Poor financial control including lack of records", "Under capitalisation", "Poor economic conditions",
       "Poor management of accounts receivable"]
INDS = ["All industries", "Construction", "Hospitality (accommodation & food)", "Retail trade", "Other services (e.g. repairs, salons)",
        "Transport & warehousing", "Professional services", "Manufacturing", "Labour hire", "Health care & social assistance"]
specs["11_bar_failure_causes"] = {
  "$schema": S, "description": "Bar chart with comparison ticks: most-nominated causes of company failure in liquidators' reports (ASIC Series 3.1, 2024–25). Pick an industry from the menu.",
  "data": {"url": "data/failure_causes.csv", "format": {"type": "csv", "parse": {"pct_of_reports": "number"}}},
  "params": [{"name": "industry", "value": "Hospitality (accommodation & food)",
              "bind": {"input": "select", "options": INDS, "name": "Industry: "}}],
  "transform": [{"filter": {"field": "cause", "oneOf": TOP}},
                {"calculate": "replace(replace(datum.cause, ' including lack of records', ' (incl. no records)'), 'Under capitalisation', 'Not enough start-up capital')", "as": "cause_label"}],
  "width": "container", "height": 330,
  "encoding": {"y": {"field": "cause_label", "type": "nominal", "title": None, "sort": [c.replace(' including lack of records', ' (incl. no records)').replace('Under capitalisation', 'Not enough start-up capital') for c in TOP],
                     "axis": {"labelFontSize": 14, "labelLimit": 300, "domain": False, "ticks": False}},
               "x": {"field": "pct_of_reports", "type": "quantitative", "title": "% of liquidator reports naming this cause", "scale": {"domain": [0, 80]}}},
  "layer": [
    {"transform": [{"filter": "datum.industry === industry"}],
     "mark": {"type": "bar", "color": TERRA, "height": {"band": 0.62}},
     "encoding": {"tooltip": [{"field": "industry", "title": "Industry"}, {"field": "cause", "title": "Cause"},
                              {"field": "pct_of_reports", "title": "% of reports"}, {"field": "reports_nominating", "title": "Reports", "format": ","}]}},
    {"transform": [{"filter": "datum.industry === industry"}],
     "mark": {"type": "text", "align": "left", "dx": 6, "fontSize": 13, "fontWeight": 600, "color": INK},
     "encoding": {"text": {"field": "pct_of_reports", "format": ".0f"}}},
    {"transform": [{"filter": "datum.industry === 'All industries'"}],
     "mark": {"type": "tick", "color": INK, "thickness": 3, "size": 26},
     "encoding": {"tooltip": [{"field": "cause", "title": "Cause"}, {"field": "pct_of_reports", "title": "All industries (%)"}]}}]}

MONTHS = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"]
specs["12_calendar_heatmap_insolvency"] = {
  "$schema": S, "description": "Calendar heatmap: companies entering external administration for the first time, each month (ASIC Series 1, data to 27 September 2026).",
  "data": {"url": "data/insolvencies_monthly.csv", "format": {"type": "csv", "parse": {"companies": "number", "calendar_year": "number"}}},
  "width": "container", "height": 300,
  "encoding": {"x": {"field": "month", "type": "ordinal", "sort": MONTHS, "title": None,
                     "axis": {"orient": "top", "labelAngle": 0, "domain": False, "ticks": False}},
               "y": {"field": "financial_year", "type": "ordinal", "title": "Financial year",
                     "axis": {"domain": False, "ticks": False}},
               "tooltip": [{"field": "month", "title": "Month"}, {"field": "calendar_year", "title": "Year", "format": "d"},
                           {"field": "companies", "title": "Companies entering insolvency"}]},
  "layer": [
    {"mark": {"type": "rect", "stroke": "#faf7f2", "strokeWidth": 2},
     "encoding": {"color": {"field": "companies", "type": "quantitative", "title": "Companies per month",
                            "scale": {"domain": [0, 1800], "range": ["#f6efe3", "#8f2f12"]},
                            "legend": {"orient": "bottom", "direction": "horizontal", "gradientLength": 260}}}},
    {"mark": {"type": "text", "fontSize": 12},
     "encoding": {"text": {"field": "companies"},
                  "color": {"condition": {"test": "datum.companies > 900", "value": "#ffffff"}, "value": INK}}}]}

for name, spec in specs.items():
    with open(os.path.join(OUT, name + ".vl.json"), "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
print(len(specs), "specs written")
