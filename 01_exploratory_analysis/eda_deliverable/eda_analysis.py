"""
EDA for the problem statement: descriptive statistics + the six figures used in the
EDA report, the slide dashboard and the one-page infographic.

Run from the repo root:  python 01_exploratory_analysis/eda_deliverable/eda_analysis.py
Writes figures/*.png and stats.json next to this file. Uses value_clean only; never fills gaps.
"""
import json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
R = REPO / "data" / "cleaned_v2"
C = R / "Controller Data (cleaned)"; O = R / "05 Operations Context (cleaned)"; D = R / "00 Cleaning Documentation"
FIG = HERE / "figures"; FIG.mkdir(exist_ok=True)
rd = lambda f: pd.read_csv(f, low_memory=False, keep_default_na=False, na_values=[""])

# ---- style: gray context, one blue focus, red reserved for the 41 F / limit lines ----
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
FOCUS, CONTEXT, LIMIT, ACCENT2 = "#2a78d6", "#b9b8b2", "#d03b3b", "#eb6834"
plt.rcParams.update({
    "font.family": "Liberation Sans", "font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlecolor": INK, "axes.titlelocation": "left",
    "figure.dpi": 200, "savefig.bbox": "tight", "lines.linewidth": 2})

def save(fig, name):
    fig.savefig(FIG / f"{name}.png", facecolor="white")
    for ax in fig.axes: ax.set_title("")          # deck copy: the slide header carries the point
    fig.savefig(FIG / f"{name}_notitle.png", facecolor="white"); plt.close(fig)

S = {}  # all statistics go here -> stats.json

# =================================================================== LOAD
H = {p: rd(C / f"Plant {p}" / f"Plant{p}_hourly_long.csv") for p in "ABC"}
DS = {p: rd(C / f"Plant {p}" / f"Plant{p}_daily_summary.csv") for p in "ABC"}
INV = {p: rd(C / f"Plant {p}" / f"Plant{p}_point_inventory.csv") for p in "ABC"}
COV = {p: rd(C / f"Plant {p}" / f"Plant{p}_coverage.csv") for p in "ABC"}
MAIN = {"A": "System Monitor Points", "B": "Area Temperatures And Vessels", "C": "Temperature Report"}

# =================================================================== 1. DATASET OVERVIEW
ov = []
for p in "ABC":
    h, inv, cov = H[p], INV[p], COV[p]
    meas = h[~h.is_setpoint]
    full = cov[cov.month_type == "full month"]; june = cov[cov.month_type != "full month"]
    ov.append(dict(plant=f"Plant {p}", hourly_rows=len(h), measured_rows=len(meas), points=int(inv.shape[0]),
                   measured_points=int((~inv.is_setpoint).sum()), setpoints=int(inv.is_setpoint.sum()),
                   days_with_data=int(h.date.nunique()), report_groups=int(cov.report.nunique()),
                   full_month_groups_present=f"{int(full.present.sum())}/{len(full)}",
                   june_groups_present=f"{int(june.present.sum())}/{len(june)}",
                   pct_measured_flagged=round(meas.quality_flag.notna().mean() * 100, 2)))
S["overview"] = ov
S["totals"] = dict(hourly_rows=int(sum(len(h) for h in H.values())),
                   measured_points=int(sum((~i.is_setpoint).sum() for i in INV.values())),
                   all_points=int(sum(len(i) for i in INV.values())), days="2026-04-01 to 2026-09-30 (183 days)")

# flags by type (measured points only), and the 'false emergencies' they would cause
fl = pd.concat([H[p][~H[p].is_setpoint].assign(plant=f"Plant {p}") for p in "ABC"])
ft = fl[fl.quality_flag.notna()].groupby(["quality_flag", "plant"]).size().unstack(fill_value=0)
S["flags_measured"] = {k: {kk: int(vv) for kk, vv in v.items()} for k, v in ft.to_dict("index").items()}
spt = H["B"][H["B"].quality_flag == "setpoint_unavailable"]
S["setpoint_unavailable_rows_B"] = int(len(spt))
missing = {f"Plant {p}": int(((COV[p].month_type == "full month") & ~COV[p].present).sum()) for p in "ABC"}
S["missing_report_groups_full_months"] = missing

# ---- per-point descriptive table for the main reports (modeled temperature points) ----
rows = []
for p in "ABC":
    h = H[p]; h = h[(h.report == MAIN[p]) & (~h.is_setpoint) & h.value_clean.notna()]
    g = h.groupby(["point_id", "unit"]).value_clean
    t = g.agg(n="size", mean="mean", sd="std", min="min", p05=lambda s: s.quantile(.05), median="median",
              p95=lambda s: s.quantile(.95), max="max").reset_index()
    t.insert(0, "plant", f"Plant {p}"); rows.append(t)
PT = pd.concat(rows).round(1)
PT.to_csv(HERE / "descriptive_stats_by_point.csv", index=False)

# =================================================================== 2. COLD ROOMS ABOVE 41 F
# cold room = temperature point (not ambient/engine/compressor) whose clean median sits between 30 and 41 F
cold = []
for p in "ABC":
    inv = INV[p]
    ids = inv[(inv.unit == "degF") & (~inv.is_setpoint) & inv.clean_median.between(30, 41)
              & ~inv.point_id.str.contains("ambient|engine|suction|oil|discharge")].point_id
    h = H[p]; h = h[(h.report == MAIN[p]) & h.point_id.isin(ids) & h.value_clean.notna()]
    for pid, g in h.groupby("point_id"):
        lab = g.point_label.iloc[0]
        cold.append(dict(plant=f"Plant {p}", point_id=pid, label=lab, hours=len(g),
                         hours_over_41=int((g.value_clean > 41).sum()),
                         pct_over_41=round((g.value_clean > 41).mean() * 100, 2),
                         median=round(g.value_clean.median(), 1), p95=round(g.value_clean.quantile(.95), 1)))
CR = pd.DataFrame(cold).sort_values("pct_over_41", ascending=False)
S["cold_rooms"] = dict(n=len(CR), total_hours=int(CR.hours.sum()), hours_over_41=int(CR.hours_over_41.sum()),
                       pct_over_41=round(CR.hours_over_41.sum() / CR.hours.sum() * 100, 2),
                       top3_share=round(CR.hours_over_41.head(3).sum() / CR.hours_over_41.sum() * 100, 1),
                       top3=CR.head(3)[["plant", "label", "pct_over_41"]].to_dict("records"),
                       rooms_never_over=int((CR.hours_over_41 == 0).sum()))
CR.to_csv(HERE / "cold_rooms_over_41F.csv", index=False)

fig, ax = plt.subplots(figsize=(7.5, 5.2))
top = CR.head(12).iloc[::-1]
cols = [FOCUS if i >= len(top) - 3 else CONTEXT for i in range(len(top))]
ax.barh([f"{r.label}  ({r.plant[-1]})" for r in top.itertuples()], top.pct_over_41, color=cols, height=0.62)
for y, v in enumerate(top.pct_over_41):
    ax.text(v + 0.4, y, f"{v:.1f}%", va="center", color=INK2, fontsize=9)
ax.set_xlabel("Share of valid hourly readings above 41 °F (Apr–Sep 2026)"); ax.grid(axis="y", visible=False)
ax.set_title(f"Three rooms hold {S['cold_rooms']['top3_share']:.0f}% of all cold-room hours above 41 °F")
ax.text(0, -0.13, f"Top 12 of {len(CR)} cold rooms (median 30–41 °F). Plant letter in brackets. Source: Plant?_hourly_long.csv, value_clean.",
        transform=ax.transAxes, fontsize=8, color=MUTED)
save(fig, "fig6_cold_rooms_over_41F")

# =================================================================== 3. DATA QUALITY: FALSE EMERGENCIES
fe = pd.DataFrame([
    ("Dead sensor reads 459.6 °F", "Plant B", int(S["flags_measured"].get("sensor_disconnected", {}).get("Plant B", 0))),
    ("Outage wrote zeros (Sep 15)", "Plant A", int((H["A"].quality_flag == "export_truncated_zero_fill").sum())),
    ("Impossible values (Back Dock, tank level)", "Plant A, C", int(sum((H[p].quality_flag == "implausible_value").sum() for p in "ABC"))),
    ("Stuck sensor, flat for 7 days", "Plant A", int(S["flags_measured"].get("stuck_value", {}).get("Plant A", 0))),
], columns=["issue", "plant", "readings"])
S["bad_readings"] = fe.to_dict("records")
S["bad_readings_total"] = int(fe.readings.sum())
fig, ax = plt.subplots(figsize=(7.5, 3.8))
f2 = fe.iloc[::-1]
ax.barh([f"{r.issue}  ({r.plant.replace('Plant ', '')})" for r in f2.itertuples()], f2.readings,
        color=[FOCUS if "Dead" in i else CONTEXT for i in f2.issue], height=0.6)
for y, v in enumerate(f2.readings):
    ax.text(v + 100, y, f"{v:,}", va="center", color=INK2, fontsize=9)
ax.set_xlabel("Hourly readings that are invalid (Apr–Sep 2026)"); ax.grid(axis="y", visible=False)
ax.set_xlim(0, f2.readings.max() * 1.15)
ax.set_title(f"{S['bad_readings_total']:,} hourly readings are broken sensors or outages, not plant conditions")
ax.text(0, -0.2, f"Excludes {S['setpoint_unavailable_rows_B']:,} Plant B setpoint readings that were never exported. Source: quality_flag, cleaning_log C07–C14.",
        transform=ax.transAxes, fontsize=8, color=MUTED)
save(fig, "fig1_bad_data")

# =================================================================== 4. JUNE 9 SUDDEN EVENT (Plant A)
h = H["A"]; j = h[(h.date == "2026-06-09") & (h.report == MAIN["A"])].pivot(index="hour", columns="point_id", values="value_clean")
rooms = ["uc_5_ready_to_eat", "uc_6_ready_to_eat", "uc_7_ready_to_eat", "uc_8_ready_to_eat"]
ds = DS["A"]; s9 = ds[(ds.date == "2026-06-09") & (ds.report == MAIN["A"]) & ds.point_id.isin(rooms)]
S["june9"] = dict(receiver_zero_hours=int((j.hpr_v1_level <= 1).sum()), first_zero_hour=int(j.index[(j.hpr_v1_level <= 1)][0]),
                  discharge_08_09_10=[float(j.discharge_pressure[x]) for x in (8, 9, 10)],
                  rooms_over_41_at_10=int((j.loc[10, rooms] > 41).sum()),
                  peak_hourly=float(j.loc[:, rooms].max().max()), peak_summary=float(s9.high_raw.max()),
                  peak_summary_point=s9.loc[s9.high_raw.idxmax(), "point_label"], peak_summary_time=s9.loc[s9.high_raw.idxmax(), "high_time"])
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.5, 5.2), sharex=True, gridspec_kw=dict(height_ratios=[1, 1.5], hspace=0.25))
a1.axvspan(9, 13, color="#f0efec", zorder=0); a2.axvspan(9, 13, color="#f0efec", zorder=0)
a1.plot(j.index, j.hpr_v1_level, color=FOCUS); a1.set_ylabel("Receiver level, %"); a1.set_ylim(-2, 40)
a1.text(11, 33, "Receiver at 0%\n09:00–13:00", ha="center", fontsize=9, color=INK)
for r in rooms:
    a2.plot(j.index, j[r], color=FOCUS if r == "uc_6_ready_to_eat" else CONTEXT, lw=2 if r == "uc_6_ready_to_eat" else 1.5)
a2.axhline(41, color=LIMIT, lw=1.2, ls="--"); a2.text(23.3, 41.5, "41 °F limit", color=LIMIT, fontsize=8, ha="right")
a2.text(10.7, 53.3, "UC-6 52.8 °F", fontsize=8, color=INK, ha="left")
a2.text(0.2, 49, "Gray: UC-5, UC-7, UC-8", fontsize=8, color=INK2)
a2.set_ylabel("Ready-to-eat cooler, °F"); a2.set_xlabel("Hour of day, 9 June 2026 (real data)"); a2.set_xticks(range(0, 24, 3))
a1.set_title("June 9: the receiver emptied and four RTE coolers crossed 41 °F within an hour")
a2.text(0, -0.3, "Plant A, System Monitor report, hourly values. Summary-line peaks at 10:46: UC-6 54.6 °F, UC-5 53.3 °F. Found only in next morning's review.",
        transform=a2.transAxes, fontsize=8, color=MUTED)
save(fig, "fig2_june9_sudden")

# =================================================================== 5. 02:45 FREEZER SPIKE (slow build)
q = ds[(ds.point_id == "uf_3_qfm") & (ds.report == MAIN["A"])].copy(); q["d"] = pd.to_datetime(q.date)
S["qfm"] = dict(days=len(q), days_high_at_0245=int((q.high_time == "02:45").sum()),
                june=q[q.date.str.startswith("2026-06")][["date", "high_raw", "hourly_max_clean"]].to_dict("records"),
                mean_gap_summary_vs_hourly=round(float((q.high_raw - q.hourly_max_clean).mean()), 1),
                apr_may_mean_high=round(float(q[q.d < "2026-06-01"].high_raw.mean()), 1))
wk = q.set_index("d").high_raw.resample("W-MON", label="left", closed="left").mean()
S["qfm"]["weekly_mean_high"] = {k.strftime("%Y-%m-%d"): round(v, 1) for k, v in wk.dropna().items()}
fig, ax = plt.subplots(figsize=(7.5, 4.0))
sim = q[~q.date.str.startswith("2026-06")]; real = q[q.date.str.startswith("2026-06")]
ax.scatter(sim.d, sim.high_raw, s=10, color=CONTEXT, label="Simulated months", zorder=2)
ax.plot(real.d, real.high_raw, "-o", color=FOCUS, ms=5, lw=1.5, label="Real June days", zorder=3)
ax.axhline(18, color=INK2, lw=1, ls=":"); ax.set_ylim(15, 52); ax.text(q.d.min(), 16.2, "18 °F setpoint", ha="left", fontsize=8, color=INK2)
ax.annotate("Thermostat swap 7/15", xy=(pd.Timestamp("2026-07-15"), 24), xytext=(pd.Timestamp("2026-07-20"), 42),
            fontsize=8, color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
ax.annotate("Returns in Sept", xy=(pd.Timestamp("2026-09-20"), 26), xytext=(pd.Timestamp("2026-08-25"), 38),
            fontsize=8, color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
ax.set_ylabel("Daily high, °F (controller summary line)"); ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.legend(frameon=False, loc="upper left", fontsize=8)
ax.set_title("The 02:45 freezer spike doubled in June and crept back after the fix")
ax.text(0, -0.17, f"Plant A UF-3 QFM. The daily high fell at 02:45 on {S['qfm']['days_high_at_0245']} of {len(q)} days; the hourly values miss the peak by {S['qfm']['mean_gap_summary_vs_hourly']} °F on average.",
        transform=ax.transAxes, fontsize=8, color=MUTED)
save(fig, "fig3_qfm_0245_spike")

# =================================================================== 6. ENGINE ROOM VS WEATHER
er = h[(h.report == MAIN["A"]) & h.point_id.isin(["uc_1_engine_room", "ambient_temperature"])].pivot_table(index="date", columns="point_id", values="value_clean", aggfunc="mean")
er.index = pd.to_datetime(er.index); er["gap"] = er.uc_1_engine_room - er.ambient_temperature
jas = er[(er.index >= "2026-07-01")]
base = er[er.index < "2026-06-01"].gap
S["engine"] = dict(gap_apr_may_median=round(float(base.median()), 1), gap_apr_may_p95=round(float(base.quantile(.95)), 1),
                   gap_0813=round(float(er.gap.get(pd.Timestamp("2026-08-13"), np.nan)), 1),
                   gap_0820=round(float(er.gap.get(pd.Timestamp("2026-08-20"), np.nan)), 1),
                   gap_0824=round(float(er.gap.get(pd.Timestamp("2026-08-24"), np.nan)), 1),
                   ambient_0813=round(float(er.ambient_temperature.get(pd.Timestamp("2026-08-13"), np.nan)), 1),
                   ambient_0820=round(float(er.ambient_temperature.get(pd.Timestamp("2026-08-20"), np.nan)), 1),
                   corr_engine_ambient_apr_may=round(float(er[er.index < "2026-06-01"][["uc_1_engine_room", "ambient_temperature"]].corr().iloc[0, 1]), 2))
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.5, 5.0), sharex=True, gridspec_kw=dict(hspace=0.25))
for a in (a1, a2): a.axvspan(pd.Timestamp("2026-08-09"), pd.Timestamp("2026-08-26"), color="#f0efec", zorder=0)
a1.plot(jas.index, jas.ambient_temperature, color=CONTEXT, lw=1.5); a1.set_ylabel("Outdoor, °F (daily mean)")
a1.text(pd.Timestamp("2026-08-17"), 71, "Heat wave 8/13,\nthen cooler", fontsize=8, ha="center", color=INK2)
a2.plot(jas.index, jas.gap, color=FOCUS); a2.axhline(S["engine"]["gap_apr_may_p95"], color=INK2, lw=1, ls=":")
a2.text(jas.index.max(), S["engine"]["gap_apr_may_p95"] + 0.5, "Apr–May 95th pct", fontsize=8, ha="right", color=INK2)
a2.text(pd.Timestamp("2026-08-17"), 9.2, "EF-2 fan failing\n(fixed 8/26)", fontsize=8, ha="center", color=INK)
a2.set_ylabel("Engine room minus outdoor, °F"); a2.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
a1.set_title("Engine room heat is a fault only when it outruns the weather")
a2.text(0, -0.25, f"Plant A daily means, Jul–Sep (simulated). On 8/20 it was {S['engine']['ambient_0820']} °F outside and the gap was +{S['engine']['gap_0820']} °F.",
        transform=a2.transAxes, fontsize=8, color=MUTED)
save(fig, "fig4_engine_vs_weather")

# =================================================================== 7. ALARM FATIGUE
al = rd(O / "controller_alarm_history_2026-04_to_09.csv"); al["start"] = pd.to_datetime(al.alarm_start)
weeks = 26.1
bp = al.groupby(["plant", "point"]).size().sort_values(ascending=False).reset_index(name="n")
S["alarms"] = dict(total=len(al), unacknowledged=int((~al.acknowledged).sum()), per_week=round(len(al) / weeks, 1),
                   per_plant_week={k: round(v / weeks, 1) for k, v in al.groupby("plant").size().items()},
                   top3_share=round(bp.n.head(3).sum() / len(al) * 100, 1), top3=bp.head(3).to_dict("records"),
                   median_duration_min=float(al.duration_min.median()), n_points=len(bp))
# known events (real faults) with at least one controller alarm inside their window
ev = rd(D / "known_events_from_ops_records.csv")
real = ev[ev.type.str.contains("real fault|slow|combined|chronic")].copy()
# the controller point each fault shows up on (None = no alarmable point exists)
EP = {"E01": "HPR", "E02": "C-1", "E03": "QFM", "E04": "QFM", "E05": "Engine Room", "E06": "Engine Room",
      "E09": "UC-9/10", "E10": "HPR", "E11": "Pre-Weigh", "E16": "C-1", "E17": "SF-1", "E18": "C-3",
      "E23": "Queso Cup", "E24": "Protein Room Front", "E25": "Freezer"}
hit = []
for r in real.itertuples():
    pl = al[(al.plant == r.plant) & al.point.str.contains(EP.get(r.event_id, "@@"), regex=False)]
    if r.event_id == "E25": pl = pl[pl.point == "Freezer"]
    w = pl[(pl.start >= pd.Timestamp(r.start)) & (pl.start <= pd.Timestamp(r.end) + pd.Timedelta("23h59min"))]
    hit.append(len(w) > 0)
real["alarmed"] = hit
real["in_june"] = real.start.str.startswith("2026-06") & real.end.str.startswith("2026-06")
S["events"] = dict(total=len(ev), types=ev.type.value_counts().to_dict(),
                   fault_events=len(real), fault_events_with_alarm=int(real.alarmed.sum()),
                   fault_events_no_alarm=real[~real.alarmed].event_id.tolist(),
                   fault_events_alarmed=real[real.alarmed].event_id.tolist(),
                   fault_events_outside_june=int((~real.in_june).sum()),
                   fault_events_outside_june_no_alarm=real[(~real.alarmed) & ~real.in_june].event_id.tolist())
fig, ax = plt.subplots(figsize=(7.5, 4.2))
b = bp.head(8).iloc[::-1]
ax.barh([f"{r.point}  ({r.plant[-1]})" for r in b.itertuples()], b.n, color=[FOCUS if i >= len(b) - 3 else CONTEXT for i in range(len(b))], height=0.6)
for y, v in enumerate(b.n): ax.text(v + 2, y, f"{v}", va="center", color=INK2, fontsize=9)
ax.set_xlabel("Controller alarms, Apr–May and Jul–Sep 2026"); ax.grid(axis="y", visible=False)
ax.set_title(f"Three chronic rooms raise {S['alarms']['top3_share']:.0f}% of the {len(al)} controller alarms")
ax.text(0, -0.17, f"{S['alarms']['per_week']} alarms a week across 3 plants (target: ≤2 false alerts per plant per week); {S['alarms']['unacknowledged']} never acknowledged. Source: controller_alarm_history.",
        transform=ax.transAxes, fontsize=8, color=MUTED)
save(fig, "fig5_alarm_fatigue")

# =================================================================== 8. OPS + REVIEW STATS
dd = rd(O / "dock_door_events_2026-04_to_09.csv"); dd["opened"] = pd.to_datetime(dd.opened)
d4 = dd[(dd.plant == "Plant A") & (dd.door == "D4") & (dd.carrier == "Carrier K")]
S["dock"] = dict(events=len(dd), median_open_min=float(dd.open_minutes.median()), p95_open_min=round(float(dd.open_minutes.quantile(.95)), 1),
                 carrierK_D4_before=round(float(d4[d4.opened < "2026-07-06"].open_minutes.mean()), 1),
                 carrierK_D4_after=round(float(d4[d4.opened >= "2026-07-06"].open_minutes.mean()), 1))
wo = rd(O / "cmms_work_orders_2026-04_to_09.csv")
S["work_orders"] = dict(total=len(wo), by_type=wo.wo_type.value_counts().to_dict(), open=int((wo.status != "Completed").sum()))
sl = rd(O / "operator_shift_log_2026-04_to_09.csv"); S["shift_log_entries"] = len(sl)
det = rd(O / "ammonia_detector_events_2026-04_to_09.csv")
S["detectors"] = dict(events=len(det), max_ppm=float(det.peak_ppm.max()), any_over_warning=int((det.peak_ppm >= 25).sum()),
                      gd_a_04_by_month=det[det.detector_id == "GD-A-04"].timestamp.str[:7].value_counts().sort_index().to_dict())
rc = rd(O / "receiving_log_2026-04_to_09.csv")
S["receiving"] = dict(receipts=len(rc), temp_checked=int(rc.temp_applicable.sum()), disposition=rc.disposition.value_counts().to_dict())
wx = rd(O / "weather_service_hourly_2026-04_to_09.csv")
S["weather"] = {p: dict(mean=round(float(g.temp_F.mean()), 1), max=float(g.temp_F.max())) for p, g in wx.groupby("plant")}
rv = rd(D / "review_claims_check.csv")
S["reviews"] = dict(numbers_checked=len(rv), exact=int((rv.status == "MATCH").sum()), approx=int((rv.status != "MATCH").sum()), text_errors=2)
S["ops_files"] = {f.name: int(len(rd(f))) for f in sorted(O.glob("*.csv"))}

json.dump(S, open(HERE / "stats.json", "w"), indent=2, default=str)
print(json.dumps(S, indent=1, default=str)[:6000])

# =================================================================== 9. KEY-POINT TABLE FOR THE REPORT
SEL = {"A": [("uc_5_ready_to_eat", MAIN["A"]), ("uc_6_ready_to_eat", MAIN["A"]), ("uc_3_4_pre_weigh", MAIN["A"]), ("uf_3_qfm", MAIN["A"]),
             ("hpr_v1_level", MAIN["A"]), ("discharge_pressure", MAIN["A"]), ("uc_1_engine_room", MAIN["A"]), ("ambient_temperature", MAIN["A"])],
       "B": [("uc_8_fin_goods_cooler", MAIN["B"]), ("uf_1_ingr_freezer", MAIN["B"]), ("sf_1_spiral_freezer_1", MAIN["B"]), ("discharge_pressure", MAIN["B"]),
             ("engine_room_temp", "Valve Group Report w/Setpoints"), ("motor_load_c01", "Compressor 1 Readings"), ("motor_load_c03", "Compressor 3")],
       "C": [("bulk_cooler_1", MAIN["C"]), ("queso_cup_chiller", MAIN["C"]), ("protein_room_front", MAIN["C"]), ("freezer", MAIN["C"]), ("ambient_air", MAIN["C"])]}
kp = []
for p, lst in SEL.items():
    h = H[p]
    for pid, rep in lst:
        g = h[(h.point_id == pid) & (h.report == rep)]
        v = g.value_clean.dropna()
        if v.empty: print("MISSING", p, pid, rep); continue
        kp.append(dict(plant=f"Plant {p}", point=g.point_label.iloc[0], unit=g.unit.iloc[0], n=int(len(v)), pct_valid=round(len(v) / len(g) * 100, 1),
                       mean=round(v.mean(), 1), sd=round(v.std(), 1), min=round(v.min(), 1), p05=round(v.quantile(.05), 1),
                       median=round(v.median(), 1), p95=round(v.quantile(.95), 1), max=round(v.max(), 1)))
S["key_points"] = kp
# monthly mean of cold-room temperature (seasonality / real-vs-simulated seam)
mm = []
for p in "ABC":
    ids = CR[CR.plant == f"Plant {p}"].point_id
    h = H[p]; h = h[(h.report == MAIN[p]) & h.point_id.isin(ids)]
    mm.append(h.groupby(h.date.str[:7]).value_clean.mean().round(1).rename(f"Plant {p}"))
S["cold_room_monthly_mean"] = pd.concat(mm, axis=1).to_dict("index")
wxm = wx.groupby([wx.timestamp_local.str[:7], "plant"]).temp_F.mean().round(1).unstack()
S["weather_monthly_mean"] = wxm.to_dict("index")
json.dump(S, open(HERE / "stats.json", "w"), indent=2, default=str)

# =================================================================== 10. RAW -> CLEAN (before / after)
n_clean = int(sum(len(h) for h in H.values()))
n_dup = 474 * 24                                              # cleaning_log C06: 474 byte-identical duplicate blocks
n_usable = int(sum(h.value_clean.notna().sum() for h in H.values()))
blank = {f"Plant {p}": int(H[p].value_clean.isna().sum()) for p in "ABC"}
S["raw_to_clean"] = dict(raw_values=n_clean + n_dup, duplicates_removed=n_dup, clean_values=n_clean, usable=n_usable,
                         usable_pct=round(n_usable / n_clean * 100, 1), blanked=n_clean - n_usable,
                         blanked_pct=round((n_clean - n_usable) / n_clean * 100, 1), blanked_setpoints=S["setpoint_unavailable_rows_B"],
                         blanked_by_plant=blank, raw_blocks=30284, clean_blocks=30284 - 474, raw_files=511, clean_files=12,
                         ops_rows=26440)
rc = S["raw_to_clean"]
fig, ax = plt.subplots(figsize=(7.5, 3.4))
labs = ["Raw hourly values\n(511 text exports)", "After removing\nexact duplicates", "Usable\n(value_clean filled)"]
vals = [rc["raw_values"], rc["clean_values"], rc["usable"]]
ax.barh(labs[::-1], vals[::-1], color=[FOCUS, CONTEXT, CONTEXT], height=0.58)
for y, v in enumerate(vals[::-1]):
    ax.text(v - 8000, y, f"{v:,}", va="center", ha="right", color="white", fontsize=10, fontweight="bold")
ax.text(rc["clean_values"] + 6000, 1, f"−{rc['duplicates_removed']:,} duplicates", va="center", fontsize=9, color=INK2)
ax.text(rc["usable"] + 6000, 0, f"−{rc['blanked']:,} blanked ({rc['blanked_setpoints']:,} are setpoints)", va="center", fontsize=9, color=INK2)
ax.set_xlim(0, rc["raw_values"] * 1.38); ax.grid(axis="y", visible=False)
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x/1000:,.0f}k"))
ax.set_xlabel("Hourly values, all three plants, Apr–Sep 2026")
ax.set_title(f"{rc['usable_pct']}% of hourly values are usable after cleaning, and nothing was guessed")
ax.text(0, -0.24, "Blanked values keep their original in value_raw. Gaps are never filled. Source: cleaning_log.csv, Plant?_hourly_long.csv.",
        transform=ax.transAxes, fontsize=8, color=MUTED)
save(fig, "fig0_raw_to_clean")
json.dump(S, open(HERE / "stats.json", "w"), indent=2, default=str)
