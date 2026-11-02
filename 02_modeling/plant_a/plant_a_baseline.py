"""
PLANT A BASELINE (v2)  -  robust hour-of-day normals + rules + drift/trend + weather-adjusted engine room.
Steps are numbered to match the written guide. Train < 2026-06-01 (Apr-May), validate June, test Jul-Sep.
Parameters were fixed before looking at Jul-Sep results and are not tuned on them.
"""
import numpy as np, pandas as pd, sys, pickle
from pathlib import Path
from scipy.stats import theilslopes
from sklearn.linear_model import HuberRegressor

HERE = Path(__file__).resolve().parent
ROOT = sys.argv[1] if len(sys.argv) > 1 else str(HERE.parents[1] / "data" / "cleaned_v2")   # cleaned v2 data folder
OUTDIR = HERE / "outputs"; OUTDIR.mkdir(exist_ok=True)
TRAIN_END = "2026-06-01"
K, MIN_RUN = 3.5, 2
FLOOR = {"degF": 0.5, "psig": 2.0, "pct_level": 2.0}

# ---- STEP 1. LOAD, KEEP CLEAN ROWS ONLY, PIVOT TO ONE COLUMN PER POINT (gaps stay NaN) ----
h = pd.read_csv(f"{ROOT}/Controller Data (cleaned)/Plant A/PlantA_hourly_long.csv", low_memory=False, keep_default_na=False, na_values=[""])
h = h[(~h.is_setpoint) & (h.report == "System Monitor Points")].copy()
h["ts"] = pd.to_datetime(h.timestamp)
unit = h.groupby("point_id").unit.first()
W = h.pivot_table(index="ts", columns="point_id", values="value_clean", aggfunc="first")
W = W.reindex(pd.date_range(W.index.min(), W.index.max(), freq="h"))
cols = [c for c in W.columns if unit[c] in FLOOR]
CONTEXT = {"ambient_temperature", "hvac_1"}
COLD = [c for c in cols if c.startswith(("uc_5","uc_6_","uc_7_","uc_8_","uc_9","uc_11","uc_13","uc_15","uc_17","uc_19","uc_21","uc_23","uc_25","uc_26","uc_3_4"))]

# ---- STEP 2. NORMAL RANGE: median + MAD by hour-of-day x weekend, trained on Apr-May ----
key = lambda ix: pd.MultiIndex.from_arrays([ix.hour, ix.dayofweek >= 5])
tr = W.loc[W.index < TRAIN_END, cols]; g = tr.groupby([tr.index.hour, tr.index.dayofweek >= 5])
med = g.median(); mad = g.agg(lambda s: np.nanmedian(np.abs(s - np.nanmedian(s))))
floor = np.array([FLOOR[unit[c]] for c in cols])
Z = pd.DataFrame((W[cols].values - med.reindex(key(W.index)).values) / np.maximum(1.4826 * mad.reindex(key(W.index)).values, floor), index=W.index, columns=cols)

events = []
def add(start, end, rule, prio, points, detail):
    events.append(dict(start=pd.Timestamp(start), end=pd.Timestamp(end), rule=rule, priority=prio, points=points, detail=detail))
def runs_of(mask):
    r = (mask != mask.shift()).cumsum()
    return [seg.index for _, seg in mask[mask].groupby(r[mask])]

# ---- STEP 3. HOURLY POINT FLAGS: robust z > K for 2 hours in a row ----
F = pd.DataFrame(False, index=W.index, columns=cols)
for c in cols:
    z = Z[c]; f = (z > K) if unit[c] == "degF" else (z.abs() > K)
    F[c] = f & f.shift(1, fill_value=False)

# ---- STEP 4. FOOD-SAFETY RULE: a cold room above 41F for 2+ hours (hourly data cannot see 30 minutes) ----
over = pd.DataFrame({c: (W[c] > 41) for c in COLD}); over = over & (over.shift(1, fill_value=False) | over.shift(-1, fill_value=False))
for c in COLD:
    for ix in runs_of(over[c]):
        add(ix[0], ix[-1] + pd.Timedelta("59min"), "food_safety_over_41F", "High", c, f"{len(ix)} h above 41F, peak {W.loc[ix, c].max():.1f}F")

# ---- STEP 5. PLANT-WIDE EVENT: 3+ points deviate together; High only if 2+ cold rooms exceed 41F, else Medium ----
core = [c for c in cols if c not in CONTEXT and not c.startswith(("v2_", "v4_"))]
hot = F[core].sum(axis=1) >= 3
for ix in runs_of(hot):
    pts = list(F.loc[ix, core].any().pipe(lambda s: s[s].index)); rooms41 = int(over.loc[ix].any().sum())
    add(ix[0], ix[-1] + pd.Timedelta("59min"), "many_points_deviate", "High" if rooms41 >= 2 else "Medium", ",".join(pts), f"{len(pts)} points, {rooms41} cold rooms >41F")

# ---- STEP 6. CRITICAL RULE: receiver level <=1% for 2+ hours during production (06-22h) ----
hpr = W["hpr_v1_level"]; z0 = (hpr <= 1.0) & hpr.index.hour.isin(range(6, 22)); z0 = z0 & (z0.shift(1, fill_value=False) | z0.shift(-1, fill_value=False))
for ix in runs_of(z0):
    add(ix[0], ix[-1] + pd.Timedelta("59min"), "receiver_zero_in_production", "Critical", "hpr_v1_level", f"{len(ix)} h at <=1%")

# ---- STEP 7. SLOW DRIFT: (a) EWMA of daily residual on OBSERVED days, (b) Theil-Sen trend over 28 days ----
def robust_scale(s, c): return max(1.4826 * np.nanmedian(np.abs(s - np.nanmedian(s))), 0.25 * FLOOR[unit[c]])
def drift_ewma(c, how, direction, lam=0.3, thr=3.0, need=2):
    s = W[c].resample("D").agg(how).dropna(); base = s[s.index < TRAIN_END]
    z = (s - base.median()) / max(1.4826 * np.nanmedian(np.abs(base - base.median())), FLOOR[unit[c]])
    z = z if direction == "up" else -z; ew, out = 0.0, []
    for v in z.values: ew = lam * v + (1 - lam) * ew; out.append(ew)
    e = pd.Series(out, index=z.index); flag = e > thr
    return [(ix[0], ix[-1], e.loc[ix].max()) for ix in runs_of(flag.rolling(need).sum() == need)]
def drift_trend(c, how, direction, window=28, min_obs=14):
    s = W[c].resample("D").agg(how).dropna(); base = s[s.index < TRAIN_END]; need = 3 * robust_scale(base, c); hits = []
    for end in s.index[s.index >= pd.Timestamp(TRAIN_END)]:
        w = s[(s.index > end - pd.Timedelta(days=window)) & (s.index <= end)]
        if len(w) < min_obs: continue
        x = (w.index - w.index[0]).days.values; sl, ic, lo, hi = theilslopes(w.values, x, 0.99)
        ch = sl * (x[-1] - x[0]); ok = (lo > 0 and ch >= need) if direction == "up" else (hi < 0 and -ch >= need)
        if ok: hits.append((end, ch))
    return hits
for c, how, direction in [("uf_3_qfm","max","up"), ("uf_4_qfm","max","up"), ("hpr_v1_level","mean","down"), ("uc_3_4_pre_weigh","mean","up")]:
    for a, b, m in drift_ewma(c, how, direction): add(a, b, "drift_ewma", "Low", c, f"EWMA z {m:.1f}")
    hits = drift_trend(c, how, direction)
    if hits:
        s_ = pd.Series({d: ch for d, ch in hits}); 
        for ix in runs_of(pd.Series(True, index=s_.index).reindex(pd.date_range(s_.index.min(), s_.index.max())).fillna(False)):
            add(ix[0], ix[-1], "drift_trend", "Low", c, f"Theil-Sen 28d change {s_.reindex(ix).max():+.1f}")

# ---- STEP 8. ENGINE ROOM vs WEATHER + LOAD: Huber regression on ambient and discharge pressure (daily means) ----
d = pd.DataFrame({"eng": W["uc_1_engine_room"].resample("D").mean(), "amb": W["ambient_temperature"].resample("D").mean(), "dp": W["discharge_pressure"].resample("D").mean()}).dropna()
trn = d[d.index < TRAIN_END]; mdl = HuberRegressor().fit(trn[["amb", "dp"]], trn.eng)
res = d.eng - mdl.predict(d[["amb", "dp"]]); rtr = res[d.index < TRAIN_END]
rz = (res - np.median(rtr)) / max(1.4826 * np.median(np.abs(rtr - np.median(rtr))), 1.0)
for ix in runs_of((rz > 4).rolling(2).sum().eq(2) | ((rz > 4) & (rz > 4).shift(-1, fill_value=False))):
    worst = res.loc[ix].max(); add(ix[0], ix[-1], "engine_room_vs_weather", "High" if worst >= 10 else "Medium", "uc_1_engine_room", f"up to +{worst:.1f}F above expected for weather and load")

for dt, v in res[res >= 10].items():          # a single very large day is High even without persistence
    add(dt, dt + pd.Timedelta("23h59min"), "engine_room_vs_weather", "High", "uc_1_engine_room", f"+{v:.1f}F above expected for weather and load")
# ---- STEP 9. MERGE REPEATS INTO EPISODES (same rule + point, gap <= 3 days) ----
E = pd.DataFrame(events).sort_values(["rule", "points", "start"]).reset_index(drop=True); out = []
for (rule, pts, prio), grp in E.groupby(["rule", "points", "priority"]):
    cur = None
    for _, r in grp.sort_values("start").iterrows():
        if cur is not None and r.start - cur["end"] <= pd.Timedelta(days=3):
            cur["end"] = max(cur["end"], r.end); cur["n_occurrences"] += 1
        else:
            if cur is not None: out.append(cur)
            cur = dict(r); cur["n_occurrences"] = 1
    if cur is not None: out.append(cur)
EP = pd.DataFrame(out).sort_values("start").reset_index(drop=True)
EP.to_csv(OUTDIR / "plant_a_baseline_events.csv", index=False)
pickle.dump(dict(W=W, Z=Z, rz=rz, res=res, d=d, EP=EP), open(OUTDIR / "plant_a_baseline_state.pkl", "wb"))   # used by score_plant_a.py
print(f"{len(events)} raw detections -> {len(EP)} episodes"); print(EP.groupby(["rule", "priority"]).size())
