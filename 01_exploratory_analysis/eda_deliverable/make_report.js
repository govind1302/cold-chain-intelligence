// EDA report (.docx): project plan, analysis plan table, descriptive statistics, preliminary findings.
// Run after eda_analysis.py:  NODE_PATH=$(npm root -g) node 01_exploratory_analysis/eda_deliverable/make_report.js
const fs = require("fs"), path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType,
  HeadingLevel, ImageRun, PageOrientation, LevelFormat, BorderStyle, Footer, PageNumber, TableLayoutType,
} = require("docx");

const HERE = __dirname;
const S = JSON.parse(fs.readFileSync(path.join(HERE, "stats.json"), "utf8"));
const X = JSON.parse(fs.readFileSync(path.join(HERE, "explanations.json"), "utf8"));
const n = (x) => Number(x).toLocaleString("en-US");
const FONT = "Calibri", INK = "0B0B0B", INK2 = "52514E", BLUE = "2A78D6", TINT = "EEF4FC", HEAD = "12263A";

// ---------------------------------------------------------------- helpers
const P = (text, o = {}) => new Paragraph({ spacing: { after: 120, line: 276 }, ...o.p, children: runs(text, o) });
function runs(text, o = {}) {
  // **bold** segments inside a string
  return String(text).split(/(\*\*[^*]+\*\*)/).filter(Boolean).map((t) =>
    t.startsWith("**") ? new TextRun({ text: t.slice(2, -2), bold: true, font: FONT, size: o.size || 22, color: o.color || INK })
                      : new TextRun({ text: t, font: FONT, size: o.size || 22, color: o.color || INK, italics: o.italics }));
}
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const B = (t, lvl = 0) => new Paragraph({ numbering: { reference: "bul", level: lvl }, spacing: { after: 60 }, children: runs(t) });
const Cap = (t) => P(t, { size: 18, color: INK2, p: { spacing: { after: 200 } } });

const border = { style: BorderStyle.SINGLE, size: 4, color: "D9D8D3" };
const borders = { top: border, bottom: border, left: border, right: border };
function table(header, rows, widths, o = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  const sz = o.size || 18;
  const cell = (t, i, isHead, shade) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA }, borders,
    shading: isHead ? { type: ShadingType.CLEAR, color: "auto", fill: HEAD } : shade ? { type: ShadingType.CLEAR, color: "auto", fill: shade } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: String(t).split("\n").map((line) => new Paragraph({
      alignment: (o.right || []).includes(i) && !isHead ? AlignmentType.RIGHT : AlignmentType.LEFT,
      children: isHead ? [new TextRun({ text: line, bold: true, color: "FFFFFF", font: FONT, size: sz })] : runs(line, { size: sz }),
    })),
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED,
    rows: [new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, i, true)) }),
           ...rows.map((r, k) => new TableRow({ cantSplit: true, children: r.map((t, i) => cell(t, i, false, o.firstColShade && i === 0 ? TINT : k % 2 ? "FAFAF9" : undefined)) }))],
  });
}
function figure(file, caption, takeaway, widthIn = 6.5) {
  const buf = fs.readFileSync(path.join(HERE, "figures", file));
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  const px = widthIn * 96, key = file.replace(".png", "");
  return [
    new Paragraph({ keepNext: true, spacing: { before: 120, after: 60 }, children: [new ImageRun({ type: "png", data: buf, transformation: { width: px, height: px * h / w },
      altText: { title: caption, description: caption, name: file } })] }),
    new Paragraph({ keepNext: true, spacing: { after: 60 }, children: runs(caption, { size: 18, color: INK2 }) }),
    ...[["Takeaway", takeaway], ["How to read it", X[key].read], ["In plain terms", X[key].plain], ["Why it matters", X[key].why]].map(([lab, txt], i, arr) =>
      new Paragraph({ keepNext: i < arr.length - 1, spacing: { before: i ? 0 : 0, after: i === arr.length - 1 ? 240 : 0, line: 276 },
        shading: { type: ShadingType.CLEAR, color: "auto", fill: TINT }, indent: { left: 0 },
        border: i === 0 ? { top: { style: BorderStyle.SINGLE, size: 24, color: TINT, space: 4 } } : i === arr.length - 1 ? { bottom: { style: BorderStyle.SINGLE, size: 24, color: TINT, space: 4 } } : undefined,
        children: [new TextRun({ text: `${lab}: `, bold: true, font: FONT, size: 21, color: BLUE }), ...runs(txt, { size: 21 })] })),
  ];
}

// ---------------------------------------------------------------- content
const ov = S.overview, ev = S.events, al = S.alarms, cr = S.cold_rooms;
const today = "5 November 2026";

const cover = [
  new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: "Cold Chain Intelligence", font: FONT, size: 22, color: INK2 })] }),
  new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("Exploratory Data Analysis and Project Plan")] }),
  P(`Team SEC02_Contextual_Odyssey · Client: Contextual IO, for Harbor Table Foods · ${today}`, { color: INK2 }),
  P("Companion files: **EDA_dashboard.pptx** (slide dashboard, one takeaway per slide) and **EDA_infographic.pdf** (one-page summary). All figures and numbers are reproducible with the scripts in 01_exploratory_analysis/eda_deliverable/.", { size: 20, color: INK2 }),
];

const exec = [
  H1("Summary"),
  P("**Guiding question (from our problem statement):** How can Harbor Table Foods automatically turn its nightly controller reports into an accurate daily review and the right alerts, so that sudden and slow-building problems are caught early, explained, and sent to the right person, without flooding staff with false alarms?"),
  P("**Overall takeaway:** the nightly reports already carry the warning signs. The hard part is separating them from broken data, weather and chronic noise. The EDA supports four design choices:"),
  B(`**Flag bad data before any rule runs.** ${n(S.bad_readings_total)} hourly readings are dead sensors, a stuck sensor, outage zeros or an impossible 130–283 °F dock reading. Plant B's dead sensor alone produces ${n(S.flags_measured.sensor_disconnected["Plant B"])} readings of 459.6 °F.`),
  B(`**Learn normal per point and hour, but keep the food-safety rule beside it.** ${cr.pct_over_41}% of cold-room hours are above 41 °F, and three rooms hold ${Math.round(cr.top3_share)}% of them. A purely learned "normal" would absorb those chronic rooms.`),
  B(`**Read the 15-minute summary line for slow trends.** The 02:45 freezer spike set the daily high on ${S.qfm.days_high_at_0245} of ${S.qfm.days} days, and hourly values miss its peak by ${S.qfm.mean_gap_summary_vs_hourly} °F on average.`),
  B(`**Explain readings with context.** Engine-room temperature tracks the weather (r = ${S.engine.corr_engine_ambient_apr_may}), so the fan fault only shows as the engine-minus-outdoor gap. Today's controller alarms run at ${al.per_week} a week, ${Math.round(al.top3_share)}% from three chronic rooms, while ${ev.fault_events_outside_june_no_alarm.length} of ${ev.fault_events_outside_june} logged faults never alarmed on their own point.`),
  P("**Important caveat:** June 2026 controller data is real (8 days for Plants A and B, 6 for Plant C). April–May and July–September are simulated, and the operations records (work orders, shift log, alarms, detectors, dock, receiving, schedule, weather, energy) cover only those simulated months. We use June as the realism check and the simulated months for scoring.", { size: 20, color: INK2 }),
];


// ---------------------------------------------------------------- 1. raw -> clean (first section)
const rc = S.raw_to_clean;
const raw = [
  H1("1. From raw data to clean data"),
  P("**Question:** what did cleaning change, add and remove, and how much of the data is usable? **Data used:** the original zip (511 controller .txt exports, 20 operations CSVs) and data/cleaned_v2/. Source: the team's raw-to-clean summary (00_raw_to_clean_summary.md), checked against data/cleaned_v2/."),
  H2("1.1 Headline numbers"),
  table(["", "Raw", "Clean"], [
    ["Controller files", "511 .txt reports", "12 CSVs (4 per plant)"],
    ["Point-blocks (one point, one report, one day)", n(rc.raw_blocks), n(rc.clean_blocks)],
    ["Hourly values", n(rc.raw_values), n(rc.clean_values)],
    ["Usable hourly values (value_clean filled)", "not separable", `${n(rc.usable)} (${rc.usable_pct}%)`],
    ["Operations files / rows", `20 / ${n(rc.ops_rows)}`, `12 / ${n(rc.ops_rows)}`],
    ["Lines that could not be parsed", "", "0"],
  ], [4360, 2500, 2500], { right: [1, 2], firstColShade: true }),
  Cap("Table 1. Raw versus clean data, all three plants, Apr–Sep 2026."),
  ...figure("fig0_raw_to_clean.png", "Figure 1. Hourly values at each cleaning step.",
    `${rc.usable_pct}% of hourly values are usable. Most of the ${rc.blanked_pct}% that is blank is Plant B setpoints that were never exported (${n(rc.blanked_setpoints)} values), not lost sensor readings. Only ${n(rc.duplicates_removed)} exact duplicates were removed; everything else is kept.`),
  H2("1.2 What was removed"),
  B(`**474 exact duplicate point-blocks (${n(rc.duplicates_removed)} hourly values).** Plant A: 314 (UC-3/4 Pre-Weigh and its setpoint exported twice). Plant B: 160 (V-2 Intercooler Pres. exported twice). Plant C: none.`),
  B("Nothing else was deleted. No operations rows were removed."),
  H2("1.3 What was blanked (kept in value_raw, blank in value_clean)"),
  table(["Flag", "Plant", "Hourly values", "Why"], [
    ["setpoint_unavailable", "B", "70,224", "Setpoint channels read 0.0 because they were never exported (all months except 4 June days)"],
    ["sensor_disconnected", "B", "8,064", "Dead sensors reading 459.6 (UC-7 Boxing And Dock, UC-4 Filling Room)"],
    ["export_truncated_zero_fill", "A", "680", "2026-09-15 hours 14–23: controller lost communication, export wrote zeros"],
    ["implausible_value", "C (372), A (1)", "373", "Back Dock sensor reading 130–283 °F; one negative vessel level"],
    ["stuck_value", "A", "312", "UC-25 flat for 7 days (2026-08-04 to 08-10)"],
    ["**Total**", "", `**${n(rc.blanked)} (${rc.blanked_pct}%)**`, ""],
  ], [2300, 1300, 1300, 4460], { right: [2] }),
  Cap(`Table 2. Blanked values by flag. Readings lost to bad data, leaving out the setpoints that were never exported, are ${n(S.bad_readings_total)} (1.3% of all hourly values); this is the count used throughout the report. By plant: Plant A ${n(rc.blanked_by_plant["Plant A"])} blank (0.4%), Plant B ${n(rc.blanked_by_plant["Plant B"])} (20.4%, almost all setpoints), Plant C ${n(rc.blanked_by_plant["Plant C"])} (0.5%).`),
  H2("1.4 What was changed (standardized)"),
  table(["Change", "Before", "After"], [
    ["Distinct point names, Plant B", "121", "85 (variable spacing collapsed)"],
    ["Distinct unit strings", "10", "7 standard units (degF, psig, psid, pct_level, pct_FLA, pct_open, cycles)"],
    ["Point-blocks with an inconsistent unit fixed", "7,742", "0"],
    ["Hourly rows re-dated (file named 06-05, data from 06-04)", "816", "0"],
    ["Dock-door close times clipped at 23:59, recomputed", "9", "0"],
    ["'24:00' schedule end times converted", "106", "0"],
    ["'(not acknowledged)' alarm placeholders", "83", "0 (boolean column)"],
    ["Detector events with location 'various'", "18", "0 (filled from asset register)"],
    ["Monthly files merged (dock doors, weather)", "10", "2"],
  ], [4300, 1100, 3960], { right: [1] }),
  Cap("Table 3. Standardization changes."),
  H2("1.5 What was added"),
  B("**Controller:** timestamp, hour, point_id, point_label, is_setpoint, measures_point (5,985 setpoint blocks linked to their measured point), compressor, value_clean, quality_flag, date_corrected, source_folder, source_file, plus cleaned and recomputed columns in the daily summaries."),
  B("**Coverage files** listing every date and report group, and why missing ones are missing."),
  B("**Operations:** 17 new columns across 8 tables (for example acknowledged, duration_min, start_ts, end_ts, temp_applicable, and plant on weather)."),
  H2("1.6 What was deliberately not changed"),
  B("34 missing report groups on 15 days in Apr–May and Jul–Sep (Plant A 6 groups on 4 days, Plant B 22 on 5 days, Plant C 6 on 6 days) are not filled."),
  B("559 receipts with blank temperatures are dry goods and packaging, so they are marked not applicable, not missing."),
  B("Back Dock drift below 130 °F, idle compressors, transfer counters, and the controller's own summary lines are kept as exported."),
  H2("1.7 What it means for EDA and modeling"),
  B("Use value_clean and rows where quality_flag is blank."),
  B("Plant B's high blank rate is setpoints, not lost measurements. Its learned normals need history, not setpoints."),
  B("Before comparing periods, check *_coverage.csv; June is a sparse sample (8 days for A and B, 6 for C)."),
];

// ---------------------------------------------------------------- project plan
const plan = [
  H1("2. High-level project plan"),
  P("Milestones run from the start of the semester project to the final presentation. Dates after today are estimates. The final demo is planned for early December 2026; we will confirm the exact date. Each milestone names the SMART goal it moves forward (G1 read every file, G2 reproduce the six reviews, G3 catch the June 9 events, the 02:45 trend by day two and at least 80% of test faults, G4 at most 2 false alerts per plant per week, G5 forecast 15% better than yesterday's values)."),
  table(["Week (2026)", "Milestone", "Key deliverables", "SMART goal", "Status"], [
    ["Oct (wk 1)", "Ingest and inventory", "Parser for both export layouts; 715k-row tidy table; point inventory; coverage calendar", "G1", "Done"],
    ["Oct (wk 2)", "Data quality and review check", "Quality flags (dead, stuck, outage, implausible); 309 review numbers traced; 26-event ground-truth map", "G1, G2", "Done"],
    ["Oct–Nov 3", "Plant A baseline", "Hour-of-day normals, rules, drift and weather models; scored against known events", "G3, G4", "Done (development result)"],
    ["Nov 2–6", "EDA and project plan", "This report, slide dashboard, infographic; analysis plan v1", "All", "This week"],
    ["Nov 9–13", "Client check-in 1; Plant B and C baselines", "Answers on thresholds, setpoints and data feed; lead/lag and spiral-freezer regimes; Plant C step and trend detection", "G3, G4", "Planned"],
    ["Nov 16–20", "Detection and context", "Event grouping, washdown/maintenance suppression, cause and severity; one scoring module for all plants", "G3, G4", "Planned"],
    ["Nov 23–27", "Reporting and alerts (short week)", "Daily review generator in the five-part format with source links; alert levels and routing; forecast baseline", "G2, G5", "Planned"],
    ["Nov 30–Dec 4", "Validation and build on Contextual", "Day-by-day replay of all months; scorecard against the success criteria; Object Types, Flows, Agents and a Site", "All", "Planned"],
    ["Early Dec", "Final presentation", "Demo, scorecard, handover notes", "All", "Planned"],
  ], [1300, 2000, 3860, 1000, 1200]),
  Cap("Table 4. Project milestones. Status as of 5 November 2026."),
];

// ---------------------------------------------------------------- analysis plan
const ap = [
  ["SQ1. Data quality and report trust: can we read every file, separate broken sensors and gaps from real readings, and check the human reviews?",
   "Parse both layouts into one table; rule-based quality flags; coverage calendar; compare each review number with the raw value",
   "Clean tidy table with quality_flag; data-health list; review error log (2 found so far)",
   "Python (pandas), regex parser",
   "**Have:** controller exports (Apr–Sep), six reviews\n**Client:** a live or hourly export to test ingest at production cadence",
   "Have (core); client for the live feed"],
  ["SQ2. Normal behavior: what does normal look like for each point, by hour of day, day type and operating regime?",
   "Robust median and MAD by hour × weekday/weekend, trained on Apr–May; regime labels (Plant B compressor lead/lag, spiral freezers on/off); correlation of co-moving points",
   "Normal band per point and hour; list of ~15 modeled points per plant; chronic-condition list",
   "Python (pandas, numpy, scipy), matplotlib",
   "**Have:** hourly values, production and sanitation schedule (simulated months)\n**Client:** Plant B setpoint history and Plant C setpoints\n**Unknown:** defrost schedule per evaporator",
   "Have (values); client (setpoints); unknown (defrost)"],
  ["SQ3. Sudden events: can we catch faults like June 9 the same day and rate their severity?",
   "Persistence rules (cold room above 41 °F for 2+ h; receiver ≤1% for 2+ h during production); count of points deviating together; replay day by day",
   "Alerts with priority and evidence; time-to-detect per known event",
   "Python, rule engine; later Contextual Flows",
   "**Have:** hourly values, ground-truth events\n**Client:** final thresholds and escalation times; June detector data (272 ppm exists only in review text); sub-hourly or alarm feed",
   "Have (data); client for thresholds and June ammonia"],
  ["SQ4. Slow trends and forecasts: can we flag slow builds like the 02:45 spike by day two, and forecast next-day readings?",
   "EWMA and Theil-Sen trend on daily summary highs and times; change-point detection (Plant C Queso chiller); same-hour-yesterday forecast baseline, then a model that beats it",
   "Low-priority trend alerts; days-to-detect for E03, E04, E10, E25; forecast error vs baseline",
   "Python (scipy, scikit-learn, statsmodels)",
   "**Have:** daily summary lines (15-minute high/low/avg), Apr–Sep history\n**Unknown:** whether longer real history (2025) exists and where it lives",
   "Have; unknown for longer history"],
  ["SQ5. Context and false alarms: which readings have a known cause, and how few alerts can we send while still catching real faults?",
   "Join alerts to sanitation windows, dock-door events, work orders and weather; engine-room-minus-ambient regression; compare current alarm log with known events",
   "Suppressed and explained alerts with reasons; false alerts per plant per week; routing table",
   "Python, SQL joins; Contextual Agents for explanations",
   "**Have:** schedule, dock, receiving, weather, work orders, shift log, alarms (simulated months)\n**Client:** June operations records, on-call roster and channels\n**Unknown:** which evaporators are switched off on purpose",
   "Have (simulated months); client (June records, roster); unknown (evaporators off)"],
];
const apSec = [
  H1("3. Analysis plan (living table, version 1)"),
  P("Each sub-question breaks down the guiding question. The last column says whether we have the data, need it from the client, or don't yet know where it lives. We will re-show this table in later updates whenever a row changes, with the change noted below it."),
  table(["Sub-question", "Analysis or method", "What it produces", "Tools", "Data needed", "Data status"],
    ap, [2700, 2600, 2200, 1350, 2900, 1210], { size: 17, firstColShade: true }),
  Cap("Table 5. Analysis plan v1, 5 November 2026. Change log: v1, first version."),
];

// ---------------------------------------------------------------- descriptive statistics
const desc = [
  H1("4. Descriptive statistics"),
  P("All statistics use **value_clean** (invalid readings blanked, gaps never filled) from data/cleaned_v2. They cover 1 April to 30 September 2026. June has only 8 sampled days for Plants A and B and 6 for Plant C."),
  H2("4.1 Dataset overview"),
  table(["Plant", "Hourly rows", "Measured points", "Setpoints", "Days with data", "Report groups", "Groups present (full months)", "Groups present (June sample)", "Measured readings flagged"],
    ov.map((o) => [o.plant, n(o.hourly_rows), o.measured_points, o.setpoints, o.days_with_data, o.report_groups, o.full_month_groups_present, o.june_groups_present, `${o.pct_measured_flagged}%`]),
    [900, 1050, 950, 900, 950, 900, 1200, 1200, 1310], { size: 17, right: [1, 2, 3, 4, 5, 8] }),
  Cap(`Table 6. ${n(S.totals.hourly_rows)} hourly rows from ${S.totals.all_points} points (${S.totals.measured_points} measured, 38 setpoints). Missing report groups in full months: Plant A ${S.missing_report_groups_full_months["Plant A"]}, Plant B ${S.missing_report_groups_full_months["Plant B"]}, Plant C ${S.missing_report_groups_full_months["Plant C"]}.`),
  H2("4.2 Data quality"),
  table(["Issue", "Plant", "Hourly readings", "What it looks like", "Handling"], [
    ["Dead sensor", "B", n(S.flags_measured.sensor_disconnected["Plant B"]), "459.6 °F every hour; summary says −459.67 (absolute zero)", "Blank, flag sensor_disconnected"],
    ["Outage zeros", "A", "680", "Every point, including setpoint channels, 0.0 after 14:00 on 15 Sep", "Blank, flag export_truncated_zero_fill"],
    ["Failing sensor", "C", n(S.flags_measured.implausible_value["Plant C"]), "Back Dock reads 130–283 °F", "Blank above 130 °F, flag implausible_value"],
    ["Stuck sensor", "A", n(S.flags_measured.stuck_value["Plant A"]), "UC-25 flat for 7 days (4–10 Aug)", "Blank, flag stuck_value"],
    ["Negative level", "A", "1", "V2 liquid level −18.8%", "Blank, flag implausible_value"],
    ["Setpoints not exported", "B", n(S.setpoint_unavailable_rows_B), "All setpoints 0.0 except 10–30 June", "Blank, flag setpoint_unavailable"],
  ], [1700, 700, 1300, 3260, 2400], { right: [2] }),
  Cap(`Table 7. ${n(S.bad_readings_total)} invalid readings, plus ${n(S.setpoint_unavailable_rows_B)} unavailable Plant B setpoint readings. The human reviews were checked: ${S.reviews.numbers_checked} numbers, ${S.reviews.exact} exact matches, ${S.reviews.approx} matches after rounding or hourly-vs-summary quoting, and ${S.reviews.text_errors} text errors in the 9 June review.`),
  H2("4.3 Key points"),
  table(["Plant", "Point", "Unit", "n", "Mean", "SD", "Min", "P5", "Median", "P95", "Max"],
    S.key_points.map((k) => [k.plant.slice(-1), k.point, k.unit.replace("pct_level", "%").replace("pct_FLA", "%FLA").replace("degF", "°F"), n(k.n), k.mean, k.sd, k.min, k.p05, k.median, k.p95, k.max]),
    [600, 2150, 700, 700, 700, 650, 700, 700, 800, 700, 760], { size: 17, right: [3, 4, 5, 6, 7, 8, 9, 10] }),
  Cap("Table 8. Hourly values, Apr–Sep 2026. Wide spreads mark regimes, not faults: spiral freezer SF-1 sits warm when off (SD 40.8 °F), and C-01 load swings with the weekly lead/lag swap. Full table for every point: descriptive_stats_by_point.csv."),
  H2("4.4 Cold rooms and the 41 °F limit"),
  P(`We define a cold room as a temperature point whose median is between 30 and 41 °F (${cr.n} rooms: 16 at Plant A, 4 at Plant B, 4 at Plant C). Across ${n(cr.total_hours)} valid room-hours, ${n(cr.hours_over_41)} (${cr.pct_over_41}%) are above 41 °F. ${cr.rooms_never_over} rooms never exceed it. The top three are ${cr.top3.map((t) => `${t.label} (${t.plant}, ${t.pct_over_41}%)`).join(", ")}.`),
  table(["Month", "Plant A cold rooms", "Plant B cold rooms", "Plant C cold rooms", "Outdoor A", "Outdoor B", "Outdoor C"],
    Object.entries(S.cold_room_monthly_mean).map(([m, v]) => {
      const w = S.weather_monthly_mean[m] || {};
      return [m + (m === "2026-06" ? " (real)" : ""), v["Plant A"], v["Plant B"], v["Plant C"], w["Plant A"] ?? "n/a", w["Plant B"] ?? "n/a", w["Plant C"] ?? "n/a"];
    }), [1500, 1300, 1300, 1300, 1260, 1250, 1450], { right: [1, 2, 3, 4, 5, 6] }),
  Cap("Table 9. Mean temperature (°F) by month. Cold rooms hold within about 1 °F while outdoor temperature swings by 16 °F, so seasonality matters for the engine room and condensers, not the rooms. There are no weather records for June."),
  H2("4.5 Operations records"),
  table(["Record", "Rows", "What stands out"], [
    ["Controller alarm history", n(al.total), `${al.per_week} per week (A ${al.per_plant_week["Plant A"]}, B ${al.per_plant_week["Plant B"]}, C ${al.per_plant_week["Plant C"]}); ${al.unacknowledged} never acknowledged; median duration ${al.median_duration_min} min`],
    ["Work orders (CMMS)", n(S.work_orders.total), `${S.work_orders.by_type.PM} preventive, ${S.work_orders.by_type.CM} corrective; ${S.work_orders.open} not completed by 30 Sep`],
    ["Operator shift log", n(S.shift_log_entries), "Free text; timestamps unreliable to the hour, so use the text and the date"],
    ["Dock door events", n(S.dock.events), `Median open ${S.dock.median_open_min} min, P95 ${S.dock.p95_open_min} min; Carrier K at door D4 went from ${S.dock.carrierK_D4_before} to ${S.dock.carrierK_D4_after} min after the seal tore (6 Jul)`],
    ["Receiving log", n(S.receiving.receipts), `${n(S.receiving.temp_checked)} temperature-checked; ${S.receiving.disposition.Rejected} rejected`],
    ["Ammonia detector events", n(S.detectors.events), `All below the 25 ppm warning (max ${S.detectors.max_ppm} ppm); GD-A-04 rising: ${Object.entries(S.detectors.gd_a_04_by_month).map(([m, c]) => `${m.slice(5)}: ${c}`).join(", ")}`],
    ["Field rounds (handheld)", n(S.ops_files["field_rounds_handheld_2026-04_to_09.csv"]), "Twice-daily manual readings; independent check on controller values"],
    ["Weather (hourly)", n(S.ops_files["weather_service_hourly_2026-04_to_09.csv"]), `Mean outdoor temperature A ${S.weather["Plant A"].mean} °F, B ${S.weather["Plant B"].mean} °F, C ${S.weather["Plant C"].mean} °F; peak ${S.weather["Plant B"].max} °F`],
    ["Schedule, energy, assets", `${S.ops_files["production_and_sanitation_schedule_2026-04_to_09.csv"]} / ${S.ops_files["utility_energy_daily_2026-04_to_09.csv"]} / ${S.ops_files["asset_register.csv"]}`, "Production and washdown windows; daily kWh; equipment list linking doors to rooms"],
  ], [2200, 1100, 6060], { right: [1] }),
  Cap(`Table 10. Operations records, Apr–May and Jul–Sep 2026. The ground truth holds ${ev.total} known events, ${ev.fault_events} of them real faults, slow builds or chronic conditions.`),
];

// ---------------------------------------------------------------- findings
const fnd = [
  H1("5. Preliminary findings"),
  P("Each figure answers part of one sub-question. Headers state the point, gray marks are context, blue marks are the focus, and the dashed red line is the 41 °F limit."),
  H2("SQ1 · Data quality"),
  ...figure("fig1_bad_data.png", "Figure 2. Invalid hourly readings by cause (excluding setpoints that were never exported).",
    `Unflagged, Plant B's dead sensor alone would fire a 459.6 °F emergency every hour for months. Quality flags must run before any detection rule, and the ${S.missing_report_groups_full_months["Plant A"] + S.missing_report_groups_full_months["Plant B"] + S.missing_report_groups_full_months["Plant C"]} missing report groups must show as "no data", never as healthy.`),
  H2("SQ3 · Sudden events"),
  ...figure("fig2_june9_sudden.png", "Figure 3. Plant A on 9 June 2026 (real data): receiver level and the four ready-to-eat coolers, hourly.",
    `The receiver read 0% for ${S.june9.receiver_zero_hours} hours and discharge pressure fell from ${S.june9.discharge_08_09_10[0]} to ${S.june9.discharge_08_09_10[2]} psig. All four coolers were above 41 °F by 10:00. A same-day persistence rule fires at 09:00; today the event surfaces in the next morning's review.`),
  H2("SQ4 · Slow trends"),
  ...figure("fig3_qfm_0245_spike.png", "Figure 4. Plant A UF-3 QFM daily high from the controller summary line.",
    `The daily high rose from about ${S.qfm.apr_may_mean_high} °F to 40–49 °F in June, dropped after the 15 July fix, and crept back to about ${S.qfm.weekly_mean_high["2026-09-28"]} °F by late September. Hourly values miss the 02:45 peak by ${S.qfm.mean_gap_summary_vs_hourly} °F, so trend rules must read the summary line.`),
  H2("SQ5 · Context: weather"),
  ...figure("fig4_engine_vs_weather.png", "Figure 5. Plant A outdoor temperature (top) and engine room minus outdoor (bottom), daily means, Jul–Sep.",
    `The hottest stretch (8/13, ${S.engine.ambient_0813} °F) had a normal gap of +${S.engine.gap_0813} °F. The failing EF-2 fan showed as +${S.engine.gap_0820} °F on 8/20, when it was only ${S.engine.ambient_0820} °F outside. Model the gap, not the raw temperature, or heat waves will page people and real faults will hide.`),
  H2("SQ5 · Context: false alarms"),
  ...figure("fig5_alarm_fatigue.png", "Figure 6. Controller alarms by point (top 8 of 12), Apr–May and Jul–Sep.",
    `Three chronic rooms raise ${Math.round(al.top3_share)}% of alarms and ${al.unacknowledged} were never acknowledged. At the same time, ${ev.fault_events_outside_june_no_alarm.length} of ${ev.fault_events_outside_june} logged faults (${ev.fault_events_outside_june_no_alarm.join(", ")}) never alarmed on their own point, including E10, the possible refrigerant loss. More thresholds will not fix this; context and trends will.`),
  H2("SQ2 · Normal behavior"),
  ...figure("fig6_cold_rooms_over_41F.png", "Figure 7. Share of valid hours above 41 °F, top 12 cold rooms.",
    `Food-safety exposure is concentrated: three rooms hold ${Math.round(cr.top3_share)}% of out-of-limit hours. A "normal" learned from history would treat them as healthy, so the model keeps a fixed 41 °F rule and a standing alert for chronic rooms beside the learned bands.`),
];

const close = [
  H1("6. Overall takeaway and next steps"),
  P("**The sudden and slow faults we checked are visible in data the plants already export.** A detector that flags bad data first, learns normal per point and hour, reads the 15-minute summary lines for slow trends, and explains readings with weather, schedules and work orders can beat today's status quo of 27 alarms a week, most of them chronic repeats."),
  B("Build Plant B baselines conditioned on compressor lead/lag and spiral-freezer regimes, and Plant C baselines with step and trend detection."),
  B("Add washdown suppression to Plant A. All 10 unexplained Plant A High alerts in Jul–Sep fall inside a scheduled UC-7 washdown."),
  B("Score every plant with one module against the 26 known events, reporting detection rate, days to detect and false alerts per plant per week."),
  H2("Questions for the client"),
  B("Is there a faster-than-nightly feed (hourly export or live alarms)? It decides whether a Critical alert can arrive in time."),
  B("Are 41 °F for 30 minutes, the escalation times and the ammonia limits final?"),
  B("Can you share Plant B setpoint history, Plant C setpoints, and the defrost schedule per evaporator?"),
  B("Do June operations records exist (detector logs, work orders, shift log)? The 272 ppm reading appears only in the review text."),
  B("Who is on call at each plant, and which channels (SMS, Slack, Teams) do they use?"),
  H2("Limitations"),
  B("Simulated months drive most findings except Figure 3 and the June points in Figure 4. Simulated patterns may be cleaner than reality; for example, Plant B cold-room monthly means do not move at all."),
  B("Rules for Plant A were adjusted after a first run, so July–September is a development result, not a held-out test."),
  B("Hourly data cannot resolve the 30-minute food-safety rule; we approximate it with two consecutive hours and use the summary line for short transients."),
];

// ---------------------------------------------------------------- document
const portrait = { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } };
const landscape = { size: { width: 12240, height: 15840, orientation: PageOrientation.LANDSCAPE }, margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 } };
const footer = new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [
  new TextRun({ text: "Cold Chain Intelligence · EDA · ", font: FONT, size: 16, color: "8A8984" }),
  new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: "8A8984" })] })] });

const doc = new Document({
  creator: "SEC02_Contextual_Odyssey", title: "Cold Chain Intelligence: EDA and Project Plan",
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", run: { font: FONT, size: 44, bold: true, color: HEAD }, paragraph: { spacing: { before: 0, after: 120 }, keepNext: true } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 30, bold: true, color: HEAD }, paragraph: { spacing: { before: 360, after: 120 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 24, bold: true, color: BLUE }, paragraph: { spacing: { before: 240, after: 80 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }] },
  sections: [
    { properties: { page: portrait }, footers: { default: footer }, children: [...cover, ...raw, ...exec, ...plan] },
    { properties: { page: landscape }, footers: { default: footer }, children: apSec },
    { properties: { page: portrait }, footers: { default: footer }, children: [...desc, ...fnd, ...close] },
  ],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(path.join(HERE, "EDA_report.docx"), b); console.log("wrote EDA_report.docx"); });
