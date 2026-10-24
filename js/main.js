// Embeds every Vega-Lite spec from /specs with one shared visual theme.
const theme = {
  font: "Work Sans", background: null, view: { stroke: null },
  axis: { labelFontSize: 13, titleFontSize: 14, titleFontWeight: 500, labelColor: "#1d3540", titleColor: "#1d3540",
          gridColor: "#ece6da", domainColor: "#9aa6a8", tickColor: "#9aa6a8", titlePadding: 10 },
  legend: { labelFontSize: 13, titleFontSize: 13, titleFontWeight: 600, labelColor: "#1d3540", titleColor: "#1d3540", labelLimit: 260 },
  title: { font: "Work Sans", fontWeight: 600, color: "#1d3540" },
  text: { font: "Work Sans", color: "#1d3540" }
};
const charts = {
  waffle: "01_waffle_size", slope: "02_slope_share", waterfall: "03_waterfall_1to4",
  choropleth: "04_map_choropleth_density", symbols: "05_map_symbols_insolvency", hex: "06_map_hex_rate",
  survival: "07_heatmap_survival", dumbbell: "08_dumbbell_entrants", legal: "09_connected_scatter_legal",
  butterfly: "10_butterfly_industry", causes: "11_bar_failure_causes", calendar: "12_calendar_heatmap_insolvency"
};
// Online (GitHub Pages): load each spec and data file from the repository.
// Offline (index.html opened from disk): browsers block those requests, so use the copy in js/bundle.js.
const offline = location.protocol === "file:" && window.DV2_SPECS;
const loader = vega.loader();
if (offline) {
  const load = loader.load.bind(loader);
  loader.load = (uri, opt) => (uri in window.DV2_DATA ? Promise.resolve(window.DV2_DATA[uri]) : load(uri, opt));
}
for (const [id, file] of Object.entries(charts)) {
  const spec = offline ? window.DV2_SPECS[file] : "specs/" + file + ".vl.json";
  vegaEmbed("#" + id, spec, { config: theme, actions: false, renderer: "svg", loader })
    .catch(err => { document.getElementById(id).textContent = "Chart failed to load: " + err.message; console.error(file, err); });
}
