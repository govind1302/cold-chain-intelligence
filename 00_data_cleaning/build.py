import pickle, re, os, shutil, glob
import pandas as pd, numpy as np
from parse import ROOT, WORK

OUT=os.environ.get("OUT_DIR","../data/cleaned_v2")
for _d in ("Controller Data (cleaned)","05 Operations Context (cleaned)"): shutil.rmtree(f"{OUT}/{_d}",ignore_errors=True)   # documentation folder is kept
CTRL=f"{OUT}/Controller Data (cleaned)"; OPS=f"{OUT}/05 Operations Context (cleaned)"; DOC=f"{OUT}/00 Cleaning Documentation"
for d in [CTRL,OPS,DOC]+[f"{CTRL}/Plant {p}" for p in "ABC"]: os.makedirs(d,exist_ok=True)

rows,_=pickle.load(open(f"{WORK}/parsed.pkl","rb"))
df=pd.DataFrame(rows)
raw_blocks=len(df)
log=[]  # (issue_id, scope, issue, rows_affected, action)
def L(i,scope,issue,n,action): log.append(dict(issue_id=i,scope=scope,issue=issue,rows_affected=int(n),action=action))

# ---------- names / units / dates ----------
df["point_orig"]=df.point
df["point"]=df.point.str.replace(r"\s+"," ",regex=True).str.strip()
n_ws=(df.point_orig!=df.point).sum()
L("C01","controller txt","Point names padded with variable internal spacing (Plant B compressor reports, fixed-width format)",n_ws,"Collapsed repeated whitespace so the same point has one name across all files")
UNIT={"Deg. F.":"degF","Deg. F":"degF","Setpoin":"degF","PSIG":"psig","Psig":"psig","% Col":"pct_level","%FLA":"pct_FLA","%":"pct_open","PSID":"psid","Cycles":"cycles"}
df["unit_orig"]=df.unit
L("C02","controller txt","Inconsistent / truncated unit strings ('Deg. F.' vs 'Deg. F', 'PSIG' vs 'Psig', 'Setpoin' used for temperature and setpoint rows)",
  df.unit.isin(["Deg. F","Setpoin","Psig"]).sum(),"Mapped all units to a standard set: degF, psig, psid, pct_level, pct_FLA, pct_open, cycles (all 'Setpoin' rows are temperatures)")
df["unit"]=df.unit.map(UNIT)
df["date"]=df.report_date
dc=df.file_date!=df.date
L("C03","controller txt","Plant B 2026-06-05 files (Area Temps, Compressor 1) carry data for 2026-06-04; file name and page header say 06-05",dc.sum(),"Used the date inside the report body as the true data date (06-04); added date_corrected flag")
df["date_corrected"]=dc
df["is_setpoint"]=df.point.str.startswith("SPT ")
df["point_label"]=df.point.replace({"V2 Liqui":"V2 Liquid Level"})
L("C04","controller txt","Truncated point name 'V2 Liqui' (Plant A)",(df.point=="V2 Liqui").sum(),"Kept original in 'point'; added readable 'point_label' (V2 Liquid Level)")
# SPT -> measured point
meas={p:set(g.loc[~g.is_setpoint,"point"]) for p,g in df.groupby("plant")}
def link(r):
    if not r.is_setpoint: return None
    s=r.point[4:]; c=meas[r.plant]
    if s in c: return s
    m=[x for x in c if x.lower().startswith(s.lower())]
    return m[0] if len(m)==1 else None
sp=df[df.is_setpoint].drop_duplicates(["plant","point"]).copy()
sp["m"]=sp.apply(link,axis=1); mp=dict(zip(zip(sp.plant,sp.point),sp.m))
df["measures_point"]=[mp.get((a,b)) if s else None for a,b,s in zip(df.plant,df.point,df.is_setpoint)]
unlinked=sp[sp.m.isna()][["plant","point"]]
L("C05","controller txt","Setpoint ('SPT ...') names are truncated and do not match the measured point name (e.g. 'SPT UC-8 Fin. Goods Co')",df.is_setpoint.sum(),
  f"Added 'measures_point' linking each setpoint row to its measured point ({len(sp)-len(unlinked)} of {len(sp)} setpoint points linked; unlinked: {unlinked.values.tolist()})")
df["point_id"]=df.point.str.lower().str.replace(r"[^a-z0-9]+","_",regex=True).str.strip("_")
df["compressor"]=df.point.str.extract(r"\bC0([1-4])$")[0].map(lambda x: f"C{x}" if isinstance(x,str) else None)

# ---------- de-duplicate ----------
key=["plant","date","report","point"]
dup=df.duplicated(key,keep="first")
L("C06","controller txt","Points exported twice in the same report (Plant A UC-3/4 Pre-Weigh & its SPT; Plant B V-2 Intercooler Pres.) - all 474 pairs byte-identical",dup.sum(),"Dropped the second copy")
df=df[~dup].copy()

# ---------- long format ----------
H=np.array([[float(x) for x in v] for v in df["values"]])
SENT=np.isclose(H,459.6)
# dead sensor: hourly 459.6 (sign dropped) <-> summary -459.67
flag=np.full(H.shape,"",dtype=object)
clean=H.copy()
def add(mask,name):
    global flag
    for i,j in zip(*np.where(mask)):
        flag[i,j]=(flag[i,j]+";"+name).strip(";")
# 1 dead sensor
add(SENT,"sensor_disconnected"); clean[SENT]=np.nan
L("C07","controller txt","Disconnected sensors: hourly value 459.6 (minus sign dropped) with summary Low/High/Avg = -459.67 (absolute zero). Plant B UC-7 Boxing And Dock (every day) and UC-4 Filling Room (11 days)",
  SENT.sum(),"value_clean set to blank; quality_flag='sensor_disconnected'; raw value kept in value_raw")
# 2 truncated export: zero-fill after cutoff
trunc=np.zeros(H.shape,bool)
for (f,rep),g in df.reset_index(drop=True).groupby(["source_file","report"]):
    if f=="PlantA_2026-09-15_nightly-export.txt":
        idx=g.index.values; trunc[np.ix_(idx,range(14,24))]=True
trunc&=(~SENT)
dfr=df.reset_index(drop=True)
add(trunc,"export_truncated_zero_fill"); clean[trunc]=np.nan
L("C08","controller txt","Plant A 2026-09-15: hours 14-23 are literal 0.0 for every point in both reports (export/controller cut-off written as zeros); the summary Average is dragged down (e.g. UC-1 Engine Room avg 41.7 F)",
  trunc.sum(),"Hours 14-23 blank in value_clean; summary Average blanked in daily file; quality_flag='export_truncated_zero_fill'")
# 3 implausible
roomtemp=(dfr.unit=="degF")&(~dfr.is_setpoint)&(dfr.compressor.isna())&(~dfr.point.str.contains("Ambient|Engine Room|HVAC"))
imp=np.zeros(H.shape,bool); imp[roomtemp.values]=H[roomtemp.values]>130
imp&=~SENT
add(imp,"implausible_value"); clean[imp]=np.nan
bd=dfr[roomtemp.values&((H>130)&~SENT).any(1)]
L("C09","controller txt","Drifting / failed room-temperature sensor: Plant C Back Dock Temp reads 130-283 F on 2026-05-20..06-04 and 2026-09-03..09-12 (a dock cannot be 280 F)",
  imp.sum(),"Hourly values >130 F on room-temperature points blanked in value_clean; quality_flag='implausible_value'. Lower drifting values (below 130 F) are NOT removed - see notes")
neg=(dfr.unit=="pct_level").values[:,None]&(H<0); add(neg,"implausible_value"); clean[neg]=np.nan
L("C10","controller txt","Negative vessel liquid level (Plant A V2 Liqui = -18.8 % on one hour)",neg.sum(),"Blanked in value_clean; quality_flag='implausible_value'")
# 3b stuck sensor: temperature point with zero variance over the whole day (not a setpoint, not compressor)
stuck=np.zeros(H.shape,bool)
flat=((H.max(1)==H.min(1))&(dfr.unit=="degF").values&(~dfr.is_setpoint).values&dfr.compressor.isna().values&(~SENT.any(1))&(~trunc.any(1)))
stuck[flat,:]=True
add(stuck,"stuck_value"); clean[stuck]=np.nan
L("C14","controller txt","Stuck sensor: Plant A UC-25 reads one constant value for all 24 hours on 2026-08-04..08-10 (work order WO-26500: 'temperature display not changing', fixed 8/11 14:00)",stuck.sum(),"value_clean blank; quality_flag='stuck_value' (only zero-variance TEMPERATURE points are flagged; idle compressors and transfer counters legitimately flat-line and are kept)")
# 4 setpoints unavailable (Plant B)
spt0=np.zeros(H.shape,bool)
for f,g in dfr[(dfr.plant=="Plant B")&dfr.is_setpoint].groupby("source_file"):
    if (H[g.index.values]==0).all(): spt0[g.index.values]=True
add(spt0,"setpoint_unavailable"); clean[spt0]=np.nan
L("C11","controller txt","Plant B setpoint channels read 0.0 on every hour in all Apr-May/Jul-Sep exports and June 1-2 (setpoints not exported); real setpoints only appear from 2026-06-10 onward",
  spt0.sum(),"value_clean blank; quality_flag='setpoint_unavailable' (learn normal from history instead)")

# long table
dfr["_i"]=np.arange(len(dfr))
long=pd.DataFrame({
 "plant":np.repeat(dfr.plant.values,24),"date":np.repeat(dfr.date.values,24),"hour":np.tile(np.arange(24),len(dfr)),
 "report":np.repeat(dfr.report.values,24),"point_id":np.repeat(dfr.point_id.values,24),"point":np.repeat(dfr.point.values,24),
 "point_label":np.repeat(dfr.point_label.values,24),"is_setpoint":np.repeat(dfr.is_setpoint.values,24),
 "measures_point":np.repeat(dfr.measures_point.values,24),"compressor":np.repeat(dfr.compressor.values,24),
 "unit":np.repeat(dfr.unit.values,24),"value_raw":H.ravel(),"value_clean":clean.ravel(),"quality_flag":flag.ravel(),
 "date_corrected":np.repeat(dfr.date_corrected.values,24),"source_folder":np.repeat(dfr.source_folder.values,24),"source_file":np.repeat(dfr.source_file.values,24)})
long["timestamp"]=pd.to_datetime(long.date)+pd.to_timedelta(long.hour,unit="h")
long["timestamp"]=long.timestamp.dt.strftime("%Y-%m-%d %H:%M")
long["source_folder"]=long.source_folder.map({"01_raw_june":"01 Raw Controller Exports","04_extended":"04 Extended History"})
cols=["plant","timestamp","date","hour","report","point_id","point","point_label","is_setpoint","measures_point","compressor","unit","value_raw","value_clean","quality_flag","date_corrected","source_folder","source_file"]
long=long[cols].sort_values(["date","report","point_id","hour"]).reset_index(drop=True)

# daily summary
S=dfr[["plant","date","report","point_id","point","point_label","is_setpoint","measures_point","compressor","unit","high","high_time","low","low_time","avg","date_corrected","source_folder","source_file"]].copy()
for c in ["high","low","avg"]: S[c]=S[c].astype(float); S=S.rename(columns={c:c+"_raw"})
cl=pd.DataFrame(clean,columns=range(24))
S["n_valid_hours"]=cl.notna().sum(1).values
S["hourly_mean_clean"]=cl.mean(1).round(2).values; S["hourly_min_clean"]=cl.min(1).values; S["hourly_max_clean"]=cl.max(1).values
dead=SENT.any(1); tr=trunc.any(1); s0=spt0.any(1)
for c in ["high","low","avg"]: S[c+"_clean"]=S[c+"_raw"]
S.loc[dead|s0|stuck.any(1),["high_clean","low_clean","avg_clean"]]=np.nan
S.loc[tr,"avg_clean"]=np.nan
S.loc[imp.any(1)|neg.any(1),["high_clean","low_clean","avg_clean"]]=np.nan
dq=pd.Series([""]*len(S))
def addd(mask,n): 
    global dq; dq=np.where(mask,np.where(dq=="",n,dq+";"+n),dq)
addd(dead,"sensor_disconnected"); addd(stuck.any(1),"stuck_value"); addd(tr,"export_truncated_zero_fill"); addd(imp.any(1)|neg.any(1),"implausible_value"); addd(s0,"setpoint_unavailable")
S["quality_flag"]=dq
S["high_time"]=S.high_time; S["low_time"]=S.low_time
S=S.sort_values(["date","report","point_id"]).reset_index(drop=True)
S=S[["plant","date","report","point_id","point","point_label","is_setpoint","measures_point","compressor","unit","high_raw","high_time","low_raw","low_time","avg_raw","high_clean","low_clean","avg_clean","n_valid_hours","hourly_mean_clean","hourly_min_clean","hourly_max_clean","quality_flag","date_corrected","source_folder","source_file"]]

# coverage
exp={"Plant A":["System Monitor Points","Valve Group Report w/Setpoints"],"Plant B":["Area Temperatures And Vessels","Compressor 1 Readings","Compressor 2","Compressor 3","Compressor 4","Valve Group Report w/Setpoints"],"Plant C":["Temperature Report"]}
alld=pd.date_range("2026-04-01","2026-09-30").strftime("%Y-%m-%d")
have=dfr.groupby(["plant","date","report"]).size().rename("n_points").reset_index()
cov=[]
for p,reps in exp.items():
    for d in alld:
        for r in reps:
            cov.append((p,d,r))
cov=pd.DataFrame(cov,columns=["plant","date","report"]).merge(have,how="left",on=["plant","date","report"])
cov["present"]=cov.n_points.notna(); cov["n_points"]=cov.n_points.fillna(0).astype(int)
cov["month_type"]=np.where(cov.date.str.startswith("2026-06"),"June sample (sparse by design)","full month")
tf=set(dfr[dfr.date=="2026-09-15"].plant.unique())
cov["note"]=""
cov.loc[(cov.plant=="Plant A")&(cov.date=="2026-09-15")&cov.present,"note"]="hours 14-23 zero-filled (export truncated)"
cov.loc[(cov.plant=="Plant B")&(cov.date=="2026-06-04")&cov.present,"note"]="data came from files named 06-05"
cov.loc[cov.date=="2026-06-03","note"]="controller reboot - no data"
cov.loc[(cov.month_type!="full month")&(~cov.present)&(cov.note==""),"note"]="not exported (June sample)"
cov.loc[(cov.month_type=="full month")&(~cov.present)&(cov.note==""),"note"]="missing from export"
L("C12","controller txt","Missing days / missing report groups (e.g. Plant A 05-09 & 09-21, Plant B 08-20, Plant C 6 days; 8 Plant B days lack compressor/valve reports)",int((~cov[cov.month_type=="full month"].present).sum()),"NOT filled or imputed; listed explicitly in *_coverage.csv so gaps are visible to modeling code")
L("C13","controller txt","Page-break headers repeat inside each report; fixed-width layout differs between folder 01 (normalized) and folder 04 (padded)",raw_blocks,"Parsed both layouts into one schema; 30,284 raw point-blocks parsed with 0 unparsed lines")

# inventory
inv=long[~long.value_raw.isna()].groupby(["plant","point_id"]).agg(point=("point","first"),point_label=("point_label","first"),report=("report",lambda s:"; ".join(sorted(set(s)))),unit=("unit","first"),is_setpoint=("is_setpoint","first"),
   measures_point=("measures_point","first"),first_date=("date","min"),last_date=("date","max"),n_days=("date","nunique"),
   n_hours=("value_raw","size"),n_flagged=("quality_flag",lambda s:(s!="").sum()),clean_median=("value_clean","median"),clean_p05=("value_clean",lambda s:s.quantile(.05)),clean_p95=("value_clean",lambda s:s.quantile(.95))).reset_index()
inv["pct_flagged"]=(inv.n_flagged/inv.n_hours*100).round(2)
for c in ["clean_median","clean_p05","clean_p95"]: inv[c]=inv[c].round(2)

for p in ["A","B","C"]:
    pl=f"Plant {p}"; d=f"{CTRL}/Plant {p}"
    long[long.plant==pl].drop(columns=["plant"]).assign(plant=pl).pipe(lambda x:x[["plant"]+[c for c in x.columns if c!="plant"]]).to_csv(f"{d}/Plant{p}_hourly_long.csv",index=False)
    S[S.plant==pl].to_csv(f"{d}/Plant{p}_daily_summary.csv",index=False)
    inv[inv.plant==pl].to_csv(f"{d}/Plant{p}_point_inventory.csv",index=False)
    cov[cov.plant==pl].drop(columns=["plant"]).to_csv(f"{d}/Plant{p}_coverage.csv",index=False)
pickle.dump((long,S,inv,cov,log),open(f"{WORK}/ctrl_out.pkl","wb"))
print(long.shape,S.shape,inv.shape,cov.shape)
print(long.quality_flag.value_counts())
print(long.groupby("plant").size())
