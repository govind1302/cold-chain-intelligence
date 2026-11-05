"""One-page static infographic built from figures/*.png and stats.json (run eda_analysis.py first)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent
S = json.load(open(HERE / "stats.json"))
INK, INK2, MUTED, FOCUS, TINT = "#0b0b0b", "#52514e", "#8a8984", "#2a78d6", "#eef4fc"
plt.rcParams["font.family"] = "Liberation Sans"

ev = S["events"]
X = json.load(open(HERE / "explanations.json"))
import textwrap
PANELS = [
    ("fig1_bad_data", "Data quality", f"Plant B's dead sensor alone produces {S['flags_measured']['sensor_disconnected']['Plant B']:,} readings of 459.6 °F. Flag these before any rule runs, or they fire as emergencies."),
    ("fig2_june9_sudden", "Sudden events", f"The receiver read 0% for {S['june9']['receiver_zero_hours']} hours and discharge pressure fell {S['june9']['discharge_08_09_10'][0]:.0f}→{S['june9']['discharge_08_09_10'][2]:.0f} psig. A same-day rule would have fired at 09:00, not the next morning."),
    ("fig3_qfm_0245_spike", "Slow trends", f"UF-3's daily high jumped from ~{S['qfm']['apr_may_mean_high']:.0f} °F to 40–49 °F in June. Hourly values miss the 02:45 peak by {S['qfm']['mean_gap_summary_vs_hourly']} °F, so trend rules must read the summary line."),
    ("fig4_engine_vs_weather", "Context: weather", f"The hottest outdoor day (8/13) had a normal gap (+{S['engine']['gap_0813']} °F). The fan fault showed on cooler days (+{S['engine']['gap_0820']} °F on 8/20). Model the gap, not the raw temperature."),
    ("fig5_alarm_fatigue", "Context: false alarms", f"{S['alarms']['per_week']} alarms a week, {S['alarms']['top3_share']:.0f}% from three chronic rooms, {S['alarms']['unacknowledged']} never acknowledged. Meanwhile {len(ev['fault_events_outside_june_no_alarm'])} of {ev['fault_events_outside_june']} logged faults never alarmed on their own point."),
    ("fig6_cold_rooms_over_41F", "Normal behavior", f"Across {S['cold_rooms']['n']} cold rooms, {S['cold_rooms']['pct_over_41']}% of hours are above 41 °F, and three rooms hold {S['cold_rooms']['top3_share']:.0f}% of them. 'Normal' learned from history would hide these chronic rooms."),
]
TILES = [
    (f"{S['totals']['hourly_rows']:,}", f"hourly readings, {S['raw_to_clean']['usable_pct']}% usable,\n3 plants, Apr–Sep 2026"),
    (f"{S['totals']['measured_points']}", "measured sensors\n(+38 setpoints)"),
    (f"{S['reviews']['numbers_checked']}/{S['reviews']['numbers_checked']}", "review numbers traced\nto raw data (2 text errors)"),
    (f"{S['alarms']['per_week']}", "alarms per week today\n(target: ≤2 per plant)"),
    (f"{S['events']['total']}", "known events to score\ndetection against"),
]

W, Hh = 11, 23.3
fig = plt.figure(figsize=(W, Hh), dpi=200); fig.patch.set_facecolor("white")
def T(x, y, s, **k): fig.text(x / W, 1 - y / Hh, s, **k)

T(0.5, 0.55, "Cold Chain Intelligence · Exploratory data analysis", fontsize=11, color=MUTED)
T(0.5, 1.15, "The nightly reports already carry the warning signs;\nthe hard part is separating them from broken data, weather and chronic noise",
  fontsize=19, fontweight="bold", color=INK, va="top", linespacing=1.15)
T(0.5, 2.05, "Harbor Table Foods, Plants A–C. June 2026 is real controller data; Apr–May and Jul–Sep are simulated, with operations records. Team SEC02_Contextual_Odyssey.",
  fontsize=9, color=INK2)

tw = (W - 1.0 - 4 * 0.2) / 5
for i, (big, lab) in enumerate(TILES):
    x = 0.5 + i * (tw + 0.2)
    ax = fig.add_axes([x / W, 1 - 3.6 / Hh, tw / W, 1.3 / Hh]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.06", fc=TINT, ec="none", transform=ax.transAxes))
    ax.text(0.08, 0.66, big, fontsize=22, fontweight="bold", color=INK, transform=ax.transAxes, va="center")
    ax.text(0.08, 0.27, lab, fontsize=8.5, color=INK2, transform=ax.transAxes, va="center", linespacing=1.2)

cw, gap = (W - 1.0 - 0.4) / 2, 0.4
# ---- section 1: raw -> clean (before / after)
rc = S["raw_to_clean"]; y = 3.95
T(0.5, y + 0.05, "FROM RAW TO CLEAN DATA", fontsize=8.5, fontweight="bold", color=FOCUS, va="top")
img = mpimg.imread(HERE / "figures" / "fig0_raw_to_clean.png"); ih = min(cw * img.shape[0] / img.shape[1], 2.5)
ax = fig.add_axes([0.5 / W, 1 - (y + 0.3 + ih) / Hh, cw / W, ih / Hh]); ax.imshow(img); ax.axis("off")
BA = [("", "Raw", "Clean"), ("Controller files", "511 .txt", "12 CSVs"), ("Point-blocks", f"{rc['raw_blocks']:,}", f"{rc['clean_blocks']:,}"),
      ("Hourly values", f"{rc['raw_values']:,}", f"{rc['clean_values']:,}"), ("Usable hourly values", "not separable", f"{rc['usable']:,} ({rc['usable_pct']}%)"),
      ("Exact duplicates removed", "", f"{rc['duplicates_removed']:,}"), ("Blanked, kept in value_raw", "", f"{rc['blanked']:,} ({rc['blanked_pct']}%)"),
      ("   of which setpoints", "", f"{rc['blanked_setpoints']:,}"), ("Operations rows", f"{rc['ops_rows']:,}", f"{rc['ops_rows']:,}"),
      ("Unparsed lines", "", "0")]
ax = fig.add_axes([(0.5 + cw + gap) / W, 1 - (y + 2.85) / Hh, cw / W, 2.5 / Hh]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, len(BA))
for i, (a_, b_, c_) in enumerate(BA):
    yy = len(BA) - i - 0.5; hd = i == 0
    if hd: ax.add_patch(FancyBboxPatch((0, yy - 0.5), 1, 1, boxstyle="square,pad=0", fc="#12263a", ec="none"))
    elif i % 2 == 0: ax.add_patch(FancyBboxPatch((0, yy - 0.5), 1, 1, boxstyle="square,pad=0", fc="#f5f5f3", ec="none"))
    col = "white" if hd else INK; wt = "bold" if hd or a_ == "Usable hourly values" else "normal"
    ax.text(0.03, yy, a_, fontsize=8.3, color=col, fontweight=wt, va="center")
    ax.text(0.66, yy, b_, fontsize=8.3, color=col, fontweight=wt, va="center", ha="right")
    ax.text(0.97, yy, c_, fontsize=8.3, color=FOCUS if a_ == "Usable hourly values" else col, fontweight=wt, va="center", ha="right")
ax2 = fig.add_axes([0.5 / W, 1 - (y + 4.2) / Hh, (W - 1) / W, 1.2 / Hh]); ax2.axis("off")
ax2.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.04", fc="#f5f5f3", ec="none", transform=ax2.transAxes))
x0 = X["fig0_raw_to_clean"]
rows = [("Takeaway", f"{rc['usable_pct']}% of hourly values are usable. Most of the {rc['blanked_pct']}% that is blank is Plant B setpoints that were never exported, not lost sensor readings. Only exact duplicates were deleted."),
        ("In plain terms", x0["short_plain"]), ("Why it matters", x0["short_why"] + " Plant B's high blank rate is missing setpoints, so its normals must be learned from history.")]
for (lab, txt), yy in zip(rows, (0.8, 0.5, 0.2)):
    ax2.text(0.015, yy, lab, fontsize=8.3, fontweight="bold", color=FOCUS if lab != "Takeaway" else INK, transform=ax2.transAxes, va="center")
    ax2.text(0.115, yy, textwrap.fill(txt, 150), fontsize=8.1, color=INK, transform=ax2.transAxes, va="center", linespacing=1.2)
top0, rowh = 3.95 + 4.5, 4.4
for k, (f, tag, call) in enumerate(PANELS):
    r, c = divmod(k, 2)
    x = 0.5 + c * (cw + gap); y = top0 + r * rowh
    T(x, y + 0.05, tag.upper(), fontsize=8.5, fontweight="bold", color=FOCUS, va="top")
    img = mpimg.imread(HERE / "figures" / f"{f}.png")
    ih = min(cw * img.shape[0] / img.shape[1], 2.5)
    ax = fig.add_axes([x / W, 1 - (y + 0.3 + ih) / Hh, cw / W, ih / Hh]); ax.imshow(img); ax.axis("off")
    ax2 = fig.add_axes([x / W, 1 - (y + 4.2) / Hh, cw / W, 1.35 / Hh]); ax2.axis("off")
    ax2.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.04", fc="#f5f5f3", ec="none", transform=ax2.transAxes))
    rows = [("Takeaway", call, INK), ("In plain terms", X[f]["short_plain"], INK), ("Why it matters", X[f]["short_why"], INK)]
    for (lab, txt, col), yy in zip(rows, (0.83, 0.5, 0.17)):
        ax2.text(0.03, yy, lab, fontsize=8.3, fontweight="bold", color=FOCUS if lab != "Takeaway" else INK, transform=ax2.transAxes, va="center")
        ax2.text(0.235, yy, textwrap.fill(txt, 66), fontsize=8.1, color=col, transform=ax2.transAxes, va="center", linespacing=1.2)

yb = top0 + 3 * rowh + 0.05
ax = fig.add_axes([0.5 / W, 1 - (yb + 0.95) / Hh, (W - 1) / W, 0.95 / Hh]); ax.axis("off")
ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.04", fc=INK, ec="none", transform=ax.transAxes))
ax.text(0.02, 0.70, "OVERALL TAKEAWAY", fontsize=9, fontweight="bold", color="#9ec5f4", transform=ax.transAxes, va="center")
ax.text(0.02, 0.33, "The sudden and slow faults we checked are visible in data the plants already export. A detector that (1) flags bad data first, (2) learns normal per point and hour,\n(3) reads the 15-minute summary lines for slow trends and (4) explains readings with weather, schedules and work orders can beat a 27-alarm-a-week status quo.",
        fontsize=9.2, color="white", transform=ax.transAxes, va="center", linespacing=1.3)
T(0.5, 23.05, "Sources: data/cleaned_v2 (controller hourly and daily summaries, operations records, cleaning documentation). Code: 01_exploratory_analysis/eda_deliverable/.",
  fontsize=7.5, color=MUTED)
fig.savefig(HERE / "EDA_infographic.png", facecolor="white"); fig.savefig(HERE / "EDA_infographic.pdf", facecolor="white")
print("ok")
