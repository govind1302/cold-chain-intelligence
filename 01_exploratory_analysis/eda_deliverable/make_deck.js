// Static data dashboard as a slide deck: one takeaway per slide, running headers that state the point.
// Run after eda_analysis.py:  node 01_exploratory_analysis/eda_deliverable/make_deck.js
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const { imageSize } = (() => { try { return require("image-size"); } catch (e) { return {}; } })();
const { applyTheme } = require("/root/.claude/skills/synced/02812373-138d-4a58-874b-33e46fa50871_49d03116-b246-4705-acfc-6f3f0d933024/pptx/scripts/apply_theme.js");

const HERE = __dirname;
const S = JSON.parse(fs.readFileSync(path.join(HERE, "stats.json"), "utf8"));
const FIG = (f) => path.join(HERE, "figures", `${f}_notitle.png`);
const ASPECT = { fig1_bad_data: 2.576, fig2_june9_sudden: 1.55, fig3_qfm_0245_spike: 1.72, fig4_engine_vs_weather: 1.459, fig5_alarm_fatigue: 2.13, fig6_cold_rooms_over_41F: 1.638 };

const THEME = {
  name: "Cold Chain", headFontFace: "Calibri", bodyFontFace: "Calibri",
  colors: { dk1: "0B0B0B", lt1: "FFFFFF", dk2: "12263A", lt2: "EEF4FC", accent1: "2A78D6", accent2: "B9B8B2",
            accent3: "D03B3B", accent4: "52514E", accent5: "8A8984", accent6: "9EC5F4", hlink: "2A78D6", folHlink: "52514E" },
};
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Cold Chain Intelligence: EDA dashboard";
pres.author = "SEC02_Contextual_Odyssey";
const C = pres.SchemeColor;

pres.defineSlideMaster({
  title: "DARK", background: { color: THEME.colors.dk2 },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.3, w: 8.8, h: 1.9, fontSize: 32, bold: true, color: C.background1, valign: "top", align: "left", margin: 0 }, text: "" } }],
});
pres.defineSlideMaster({
  title: "CONTENT", background: { color: THEME.colors.lt1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9.0, h: 0.85, fontSize: 24, bold: true, color: C.text1, valign: "top", align: "left", margin: 0 }, text: "" } },
    { text: { text: "Cold Chain Intelligence · EDA", options: { x: 0.5, y: 5.25, w: 5, h: 0.25, fontSize: 9, color: C.accent5, margin: 0 } } },
  ],
  slideNumber: { x: 9.0, y: 5.25, w: 0.5, h: 0.25, fontSize: 9, color: C.accent5, align: "right", margin: 0 },
});

// ---------------------------------------------------------------- 1 title
pres.addSection({ title: "Summary" });
let s = pres.addSlide({ masterName: "DARK", sectionTitle: "Summary" });
s.addText("The nightly reports already carry the warning signs. The hard part is separating them from broken data, weather and chronic noise", { placeholder: "title" });
s.addText("Exploratory data analysis · Harbor Table Foods, Plants A–C · Apr–Sep 2026", { x: 0.6, y: 3.55, w: 8.8, h: 0.4, fontSize: 16, color: C.accent6, margin: 0, isTextBox: true, objectName: "subtitle" });
s.addText("Team SEC02_Contextual_Odyssey · Client: Contextual IO · November 2026", { x: 0.6, y: 4.0, w: 8.8, h: 0.35, fontSize: 12, color: C.background1, margin: 0, isTextBox: true, objectName: "byline" });
s.addNotes("June 2026 controller data is real; Apr–May and Jul–Sep are simulated and come with operations records.");

// ---------------------------------------------------------------- 2 overall takeaway
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Summary" });
s.addText("Four habits separate real faults from noise, and the data to build them already exists", { placeholder: "title" });
const tiles = [
  [S.totals.hourly_rows.toLocaleString("en-US"), "hourly readings, 3 plants"],
  [String(S.totals.measured_points), "measured sensors"],
  [`${S.reviews.numbers_checked}/${S.reviews.numbers_checked}`, "review numbers traced"],
  [String(S.alarms.per_week), "alarms a week today"],
];
tiles.forEach(([big, lab], i) => {
  const x = 0.5 + i * 2.3;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.3, w: 2.1, h: 1.05, fill: { color: C.background2 }, rectRadius: 0.08, line: { type: "none" }, objectName: `tile${i}` });
  s.addText(big, { x: x + 0.15, y: 1.38, w: 1.85, h: 0.55, fontSize: 26, bold: true, color: C.text1, margin: 0, isTextBox: true, objectName: `tileBig${i}` });
  s.addText(lab, { x: x + 0.15, y: 1.93, w: 1.85, h: 0.32, fontSize: 11, color: C.accent4, margin: 0, isTextBox: true, objectName: `tileLab${i}` });
});
const habits = [
  ["1  Flag bad data first", `${(S.bad_readings_total).toLocaleString("en-US")} readings are dead or stuck sensors and outages`],
  ["2  Learn normal per point and hour", `3 rooms hold ${Math.round(S.cold_rooms.top3_share)}% of cold-room hours above 41 °F`],
  ["3  Read the summary line for slow trends", `hourly data misses the 02:45 peak by ${S.qfm.mean_gap_summary_vs_hourly} °F`],
  ["4  Explain with context", `${S.alarms.top3_share.toFixed(0)}% of alarms come from 3 chronic rooms`],
];
habits.forEach(([h, d], i) => {
  const x = 0.5 + (i % 2) * 4.6, y = 2.65 + Math.floor(i / 2) * 1.2;
  s.addText([{ text: h, options: { bold: true, fontSize: 15, color: C.accent1, breakLine: true } }, { text: d, options: { fontSize: 14, color: C.text1 } }],
    { x, y, w: 4.4, h: 1.0, margin: 0, valign: "top", isTextBox: true, objectName: `habit${i}` });
});

// ---------------------------------------------------------------- 3-8 one visual per slide
const VIS = [
  { sec: "Data quality", f: "fig1_bad_data", title: `${S.bad_readings_total.toLocaleString("en-US")} hourly readings are broken sensors or outages, not plant conditions`,
    take: "Unflagged, Plant B's dead sensor alone would fire a 459.6 °F emergency every hour for months.",
    k: [[S.flags_measured.sensor_disconnected["Plant B"].toLocaleString("en-US"), "dead-sensor hours, Plant B"], [String(S.missing_report_groups_full_months["Plant A"] + S.missing_report_groups_full_months["Plant B"] + S.missing_report_groups_full_months["Plant C"]), "report groups missing (never filled)"]],
    src: "Source: quality_flag in Plant?_hourly_long.csv; cleaning_log.csv C07–C14" },
  { sec: "Sudden events", f: "fig2_june9_sudden", title: "June 9: the receiver emptied and four ready-to-eat coolers crossed 41 °F within an hour",
    take: "A same-day rule (receiver ≤1% for 2 h in production) fires at 09:00. Today it surfaces in the next morning's review.",
    k: [[`${S.june9.receiver_zero_hours} h`, "receiver at 0% during production"], [`${S.june9.discharge_08_09_10[0].toFixed(0)}→${S.june9.discharge_08_09_10[2].toFixed(0)}`, "discharge pressure, psig (08:00→10:00)"]],
    src: "Source: PlantA_hourly_long.csv, 9 June 2026 (real data), System Monitor report" },
  { sec: "Slow trends", f: "fig3_qfm_0245_spike", title: "The 02:45 freezer spike doubled in June and crept back after the fix",
    take: "Slow faults live in the 15-minute summary line. A trend rule on daily highs catches them; an hourly threshold does not.",
    k: [[`${S.qfm.days_high_at_0245}/${S.qfm.days}`, "days whose high fell at 02:45"], [`${S.qfm.mean_gap_summary_vs_hourly} °F`, "peak missed by hourly values"]],
    src: "Source: PlantA_daily_summary.csv, UF-3 QFM high_raw / high_time" },
  { sec: "Context", f: "fig4_engine_vs_weather", title: "Engine room heat is a fault only when it outruns the weather",
    take: `The hottest day had a normal gap (+${S.engine.gap_0813} °F). The EF-2 fan fault showed on cooler days (+${S.engine.gap_0820} °F). Model the gap, not the raw temperature.`,
    k: [[String(S.engine.corr_engine_ambient_apr_may), "engine room vs outdoor correlation, Apr–May"], [`+${S.engine.gap_0824} °F`, "peak gap before the 8/26 repair"]],
    src: "Source: PlantA_hourly_long.csv daily means; WO-26499; shift log 8/9–8/20" },
  { sec: "Context", f: "fig5_alarm_fatigue", title: `Three chronic rooms raise ${S.alarms.top3_share.toFixed(0)}% of the ${S.alarms.total} controller alarms`,
    take: `Staff see ${S.alarms.per_week} alarms a week and ignored ${S.alarms.unacknowledged}. Yet ${S.events.fault_events_outside_june_no_alarm.length} of ${S.events.fault_events_outside_june} logged faults never alarmed on their own point.`,
    k: [[String(S.alarms.unacknowledged), "alarms never acknowledged"], [`${S.events.fault_events_outside_june_no_alarm.length} of ${S.events.fault_events_outside_june}`, "faults with no alarm, incl. E10 refrigerant loss"]],
    src: "Source: controller_alarm_history; known_events_from_ops_records.csv" },
  { sec: "Normal behavior", f: "fig6_cold_rooms_over_41F", title: `Three rooms hold ${Math.round(S.cold_rooms.top3_share)}% of all cold-room hours above 41 °F`,
    take: "Food-safety risk is concentrated, not spread. A 'normal' learned from history would absorb these rooms, so keep the 41 °F rule beside it.",
    k: [[`${S.cold_rooms.pct_over_41}%`, `of hours above 41 °F, ${S.cold_rooms.n} cold rooms`], [String(S.cold_rooms.rooms_never_over), "cold rooms never above 41 °F"]],
    src: "Source: Plant?_hourly_long.csv value_clean; cold room = median 30–41 °F" },
];
let lastSec = "Summary";
VIS.forEach((v, i) => {
  if (v.sec !== lastSec) { pres.addSection({ title: v.sec }); lastSec = v.sec; }
  const sl = pres.addSlide({ masterName: "CONTENT", sectionTitle: v.sec });
  sl.addText(v.title, { placeholder: "title" });
  // chart: fit inside 5.9 x 3.6 box
  const bw = 5.9, bh = 3.6, a = ASPECT[v.f];
  let w = bw, h = bw / a; if (h > bh) { h = bh; w = bh * a; }
  sl.addImage({ path: FIG(v.f), x: 0.5, y: 1.3 + (bh - h) / 2, w, h, altText: v.title, objectName: "chart" });
  // takeaway panel
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.65, y: 1.3, w: 2.85, h: 3.6, fill: { color: C.background2 }, rectRadius: 0.08, line: { type: "none" }, objectName: "panel" });
  sl.addText("TAKEAWAY", { x: 6.85, y: 1.42, w: 2.5, h: 0.25, fontSize: 10, bold: true, color: C.accent1, margin: 0, isTextBox: true, objectName: "takeLabel" });
  sl.addText(v.take, { x: 6.85, y: 1.7, w: 2.5, h: 1.45, fontSize: 13, color: C.text1, margin: 0, valign: "top", isTextBox: true, objectName: "take" });
  v.k.forEach(([big, lab], j) => {
    const y = 3.2 + j * 0.85;
    sl.addText(big, { x: 6.85, y, w: 2.5, h: 0.42, fontSize: 22, bold: true, color: C.text1, margin: 0, isTextBox: true, objectName: `kBig${j}` });
    sl.addText(lab, { x: 6.85, y: y + 0.4, w: 2.5, h: 0.35, fontSize: 10, color: C.accent4, margin: 0, isTextBox: true, objectName: `kLab${j}` });
  });
  sl.addText(v.src, { x: 0.5, y: 4.95, w: 6.0, h: 0.25, fontSize: 9, color: C.accent5, margin: 0, isTextBox: true, objectName: "source" });
});

// ---------------------------------------------------------------- 9 so what
pres.addSection({ title: "Next steps" });
s = pres.addSlide({ masterName: "DARK", sectionTitle: "Next steps" });
s.addText("Next: turn these four habits into Plant B and C baselines and score them against the 26 known events", { placeholder: "title", fontSize: 26 });
const nx = [
  ["Nov 9–13", "Client check-in: thresholds, Plant B/C setpoints, faster data feed"],
  ["Nov 16–20", "Plant B and C baselines; washdown suppression for Plant A"],
  ["Nov 23–Dec 4", "Daily review generator, forecast baseline, full replay and scoring"],
  ["Early Dec", "Final presentation and demo on the Contextual platform"],
];
nx.forEach(([d, t], i) => {
  const y = 3.25 + i * 0.5;
  s.addText(d, { x: 0.6, y, w: 1.7, h: 0.4, fontSize: 14, bold: true, color: C.accent6, margin: 0, isTextBox: true, objectName: `nd${i}` });
  s.addText(t, { x: 2.4, y, w: 7.0, h: 0.4, fontSize: 14, color: C.background1, margin: 0, isTextBox: true, objectName: `nt${i}` });
});

(async () => {
  const out = path.join(HERE, "EDA_dashboard.pptx");
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out);
})();
