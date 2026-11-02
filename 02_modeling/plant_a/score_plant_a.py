import pandas as pd, numpy as np, sys, pickle
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = sys.argv[1] if len(sys.argv) > 1 else str(HERE.parents[1] / "data" / "cleaned_v2")
pd.set_option("display.width",250); pd.set_option("display.max_rows",200); pd.set_option("display.max_colwidth",70)
EP=pd.read_csv(HERE / "outputs" / "plant_a_baseline_events.csv",parse_dates=["start","end"])
def first(rule=None,points=None,after=None,before=None,prio=None):
    m=pd.Series(True,index=EP.index)
    if rule: m&=EP.rule.isin(rule if isinstance(rule,list) else [rule])
    if points: m&=EP.points.str.contains(points)
    if after: m&=EP.end>=pd.Timestamp(after)
    if before: m&=EP.start<=pd.Timestamp(before)
    if prio: m&=EP.priority.isin(prio)
    x=EP[m].sort_values("start"); return None if x.empty else x.iloc[0]
rows=[]
def row(eid,name,onset,r,expect,note=""):
    rows.append((eid,name,onset,None if r is None else f"{r.start:%m-%d %H:%M}",None if r is None else f"{r.rule} / {r.priority}",None if r is None else round((r.start-pd.Timestamp(onset)).total_seconds()/86400,1),expect,note))
row("E01","Receiver 0% in production, rooms warm","2026-06-09 09:00",first("receiver_zero_in_production","hpr","2026-06-09","2026-06-10"),"Critical","needs 2 consecutive hours")
row("E03","02:45 QFM spike growing (June)","2026-06-01 00:00",first(["drift_ewma","drift_trend"],"uf_3_qfm","2026-06-01","2026-06-30"),"Low","3rd observed day; first June day too small to pass")
row("E04","QFM spike returns (Sept)","2026-09-07 00:00",first(["drift_ewma","drift_trend"],"uf_3_qfm","2026-09-01","2026-09-30"),"Low")
row("E05","Engine room 102F (6/30)","2026-06-30 00:00",first("engine_room_vs_weather","engine","2026-06-30","2026-06-30"),"High")
row("E06","EF-2 failing, engine room (Aug)","2026-08-09 00:00",first("engine_room_vs_weather","engine","2026-08-01","2026-08-31"),"Medium","heat wave overlaps first week")
row("E09","D4 seal + Carrier K unloads, UC-9/10","2026-07-06 00:00",first("food_safety_over_41F","uc_9_10","2026-07-06"),"High","first 2h excursion; every one follows a Carrier K unload")
row("E10","Receiver level slowly falling","2026-08-01 00:00",first(["drift_ewma","drift_trend"],"hpr","2026-07-15","2026-09-30"),"Low","sight glass remark only on 9/10")
row("E11","Chronic Pre-Weigh >41F","2026-04-01 00:00",first("food_safety_over_41F","pre_weigh","2026-04-01"),"High","chronic; should be one standing alert")
S=pd.DataFrame(rows,columns=["event","what","onset","first alert","rule / priority","days after onset","target","note"]); print(S.to_string(index=False))
# negative controls
n7=EP[(EP.start>="2026-08-04")&(EP.start<="2026-08-10 23:59")&EP.points.str.contains("uc_25")]; n8=EP[(EP.start>="2026-09-15")&(EP.start<"2026-09-16")]
print("\nNegative controls: alerts on stuck UC-25 (8/4-8/10):",len(n7),"| alerts started on 9/15 outage day:",len(n8))
# false alarms Jul-Sep
HC=EP[(EP.priority.isin(["High","Critical"]))&(EP.start>="2026-07-01")]
def cls(r):
    if "uc_9_10" in r.points: return "explained: D4/Carrier K (E09)"
    if r.rule=="many_points_deviate" and r.start.date()==pd.Timestamp("2026-07-16").date(): return "explained: D4/Carrier K (E09)"
    if "pre_weigh" in r.points or "uc_6_" in r.points: return "chronic (E11)"
    return "UNEXPLAINED"
HC=HC.assign(cls=HC.apply(cls,axis=1)); print("\nHigh/Critical episodes 7/1-9/30:"); print(HC.groupby("cls").agg(episodes=("start","size"),occurrences=("n_occurrences","sum")))
un=HC[HC.cls=="UNEXPLAINED"]; print("Unexplained detail:"); print(un[["start","rule","points","detail","n_occurrences"]].to_string(index=False))
wks=(pd.Timestamp("2026-09-30")-pd.Timestamp("2026-07-01")).days/7
print(f"\nUnexplained episodes per week: {len(un)/wks:.2f}; if every occurrence alerted: {un.n_occurrences.sum()/wks:.2f}")
print("Plant-wide events Jul-Sep:",len(EP[(EP.rule=='many_points_deviate')&(EP.start>='2026-07-01')]),"| in Apr-May:",len(EP[(EP.rule=='many_points_deviate')&(EP.start<'2026-06-01')]))

# ---- context joins (PRD R7): sanitation schedule and dock doors ----
OPS = f"{ROOT}/05 Operations Context (cleaned)"
sc = pd.read_csv(f"{OPS}/production_and_sanitation_schedule_2026-04_to_09.csv", parse_dates=["start_ts", "end_ts"])
san = sc[(sc.plant == "Plant A") & (sc.activity == "Sanitation")]
uc7 = EP[(EP.rule == "food_safety_over_41F") & EP.points.str.contains("uc_7") & (EP.start >= "2026-07-01")]
inside = sum(((san.start_ts <= r.start) & (san.end_ts >= r.start)).any() for _, r in uc7.iterrows())
print(f"\nUC-7 Jul-Sep episodes inside a scheduled washdown window: {inside} of {len(uc7)}  -> schedule suppression removes them")
dd = pd.read_csv(f"{OPS}/dock_door_events_2026-04_to_09.csv", parse_dates=["opened"])
d4 = dd[(dd.plant == "Plant A") & (dd.door == "D4")]
W = pickle.load(open(HERE / "outputs" / "plant_a_baseline_state.pkl", "rb"))["W"]
o = W["uc_9_10_cooler"] > 41; o = o & (o.shift(1, fill_value=False) | o.shift(-1, fill_value=False))
days = sorted(set(o[o & (o.index >= "2026-07-01")].index.normalize())); hit = 0
for d in days:
    f = o[o.index.normalize() == d]; f = f[f].index[0]
    near = d4[(d4.opened >= f - pd.Timedelta("4h")) & (d4.opened <= f + pd.Timedelta("1h")) & (d4.carrier == "Carrier K") & (d4.open_minutes >= 45)]
    hit += len(near) > 0
print(f"UC-9/10 days above 41F for 2h+ after 7/1: {len(days)}; preceded by a Carrier K unload (>=45 min) at door D4: {hit}")
