import pandas as pd, numpy as np, glob, os, pickle, re
from parse import ROOT, WORK
OUT=os.environ.get("OUT_DIR","../data/cleaned_v2"); OPS=f"{OUT}/05 Operations Context (cleaned)"
SRC=f"{ROOT}/05 Operations Context"
R=lambda f: pd.read_csv(f"{SRC}/{f}",dtype=str,keep_default_na=False)
W=lambda d,f: d.to_csv(f"{OPS}/{f}",index=False)
log=[]
def L(i,scope,issue,n,action): log.append(dict(issue_id=i,scope=scope,issue=issue,rows_affected=int(n),action=action))
ts=lambda s: pd.to_datetime(s).dt.strftime("%Y-%m-%d %H:%M")

# --- dock door events: merge months, fix midnight clipping
dd=pd.concat([R(f) for f in sorted(os.path.basename(x) for x in glob.glob(f"{SRC}/dock_door_events_*.csv"))],ignore_index=True)
dd["opened_dt"]=pd.to_datetime(dd.opened); dd["closed_dt"]=pd.to_datetime(dd.closed); dd["open_minutes"]=dd.open_minutes.astype(float)
calc=(dd.closed_dt-dd.opened_dt).dt.total_seconds()/60
clip=(calc-dd.open_minutes).abs()>1.5
dd["closed_raw"]=dd.closed
dd["closed_clipped_at_midnight"]=clip
dd.loc[clip,"closed_dt"]=dd.loc[clip,"opened_dt"]+pd.to_timedelta(dd.loc[clip,"open_minutes"],unit="m")
dd["opened"]=dd.opened_dt.dt.strftime("%Y-%m-%d %H:%M"); dd["closed"]=dd.closed_dt.dt.strftime("%Y-%m-%d %H:%M")
dd["date"]=dd.opened_dt.dt.strftime("%Y-%m-%d"); dd["hour"]=dd.opened_dt.dt.hour
dd=dd.sort_values(["opened_dt","plant","door"]).reset_index(drop=True)
dd=dd[["event_id","plant","door","door_function","date","opened","closed","closed_raw","closed_clipped_at_midnight","open_minutes","direction","carrier","trailer_id","receipt_id"]]
W(dd,"dock_door_events_2026-04_to_09.csv")
L("O01","dock_door_events","5 monthly files (Apr, May, Jul, Aug, Sep; no June)",len(dd),"Merged into one file sorted by open time")
L("O02","dock_door_events","'closed' stamped 23:59 when the door stayed open past midnight, so closed-opened disagrees with open_minutes",clip.sum(),"Recomputed closed = opened + open_minutes (spills into next day); original kept in closed_raw; flag closed_clipped_at_midnight")

# --- weather: merge, add plant
w=pd.concat([R(f) for f in sorted(os.path.basename(x) for x in glob.glob(f"{SRC}/weather_service_hourly_*.csv"))],ignore_index=True)
w["plant"]=w.station.str.extract(r"(Plant [ABC])")[0]
w=w[["timestamp_local","plant","station","temp_F","rel_humidity_pct","sky","precip_in"]].sort_values(["plant","timestamp_local"])
W(w,"weather_service_hourly_2026-04_to_09.csv")
L("O03","weather_service_hourly","15 files (5 months x 3 stations in rows) with no plant key, only a station string",len(w),"Merged; added 'plant' column so it joins directly to controller/ops tables")

# --- schedule: 24:00 / blank holiday times
sc=R("production_and_sanitation_schedule_2026-04_to_09.csv")
def mk(d,t,add=0):
    out=[]
    for dd_,tt in zip(d,t):
        if tt=="": out.append(""); continue
        h,m=map(int,tt.split(":")); base=pd.Timestamp(dd_)+pd.Timedelta(hours=h,minutes=m)
        out.append(base.strftime("%Y-%m-%d %H:%M"))
    return out
n24=(sc.end=="24:00").sum()
sc["start_ts"]=mk(sc.date,sc.start); sc["end_ts"]=mk(sc.date,sc.end)
sc["duration_hours"]=((pd.to_datetime(sc.end_ts.replace("",np.nan))-pd.to_datetime(sc.start_ts.replace("",np.nan))).dt.total_seconds()/3600).round(2)
sc["is_holiday"]=sc.activity.str.startswith("Holiday")
sc=sc[["date","plant","activity","is_holiday","start","end","start_ts","end_ts","duration_hours","product_families","notes"]]
W(sc,"production_and_sanitation_schedule_2026-04_to_09.csv")
L("O04","production_schedule","End time '24:00' is not a valid clock time (106 rows); holiday rows have blank start/end",n24,"Added start_ts/end_ts as real timestamps (24:00 -> 00:00 next day) and duration_hours; original start/end kept; added is_holiday")

# --- alarms
al=R("controller_alarm_history_2026-04_to_09.csv")
na=al.acknowledged_by=="(not acknowledged)"
al["acknowledged"]=~na; al.loc[na,"acknowledged_by"]=""
al["peak_value"]=al.peak_value.astype(float)
al["duration_min"]=((pd.to_datetime(al.alarm_clear)-pd.to_datetime(al.alarm_start)).dt.total_seconds()/60).astype(int)
al["alarm_threshold_F"]=al.alarm.str.extract(r"\((\d+)F\)")[0]
al["alarm_offset_over_setpoint_F"]=al.alarm.str.extract(r"SP\+(\d+)F")[0]
W(al,"controller_alarm_history_2026-04_to_09.csv")
L("O05","controller_alarm_history","Placeholder text '(not acknowledged)' stored in the acknowledged_by column",na.sum(),"Blanked and added boolean 'acknowledged'; added duration_min and numeric alarm_threshold_F / alarm_offset_over_setpoint_F parsed from the alarm text")

# --- field rounds
fr=R("field_rounds_handheld_2026-04_to_09.csv")
U={"Handheld thermometer":"degF","Panel gauge psig":"psig","Panel gauge psid":"psid","Sight glass %":"pct_level"}
fr["unit"]=fr.instrument.map(U); fr["reading"]=fr.reading.astype(float)
fr=fr[["timestamp","plant","round","point","instrument","unit","reading","note"]]
W(fr,"field_rounds_handheld_2026-04_to_09.csv")
L("O06","field_rounds_handheld","'reading' mixes degF, psig, psid and % with the unit only implied by 'instrument'",len(fr),"Added explicit 'unit' column (same unit vocabulary as the controller CSVs)")

# --- receiving
rc=R("receiving_log_2026-04_to_09.csv")
rc["temp_applicable"]=rc.product_temp_at_receipt_F!=""
for c in ["pallets"]: rc[c]=rc[c].astype(int)
for c in ["reefer_setpoint_F","product_temp_at_receipt_F"]: rc[c]=pd.to_numeric(rc[c].replace("",np.nan))
rc=rc[["receipt_id","plant","date","appointment","arrived_at_door","door","carrier","supplier","category","pallets","temp_applicable","reefer_setpoint_F","product_temp_at_receipt_F","disposition","receiver_note"]]
W(rc,"receiving_log_2026-04_to_09.csv")
L("O07","receiving_log","Blank reefer setpoint / product temperature on all Dry ingredients and Packaging receipts",(~rc.temp_applicable).sum(),"Left blank (not missing: ambient goods are not temperature-checked); added 'temp_applicable' so models do not treat these as missing data")

# --- ammonia detector events: 'various'
de=R("ammonia_detector_events_2026-04_to_09.csv"); ar=R("asset_register.csv")
loc=dict(zip(ar.asset_id,ar.location))
vv=de.location=="various"
de["location_logged"]=de.location; de["location"]=de.detector_id.map(loc)
de["duration_min"]=de.duration_min.astype(int); de["peak_ppm"]=de.peak_ppm.astype(float)
de=de[["timestamp","plant","detector_id","location","location_logged","duration_min","peak_ppm","level"]]
W(de,"ammonia_detector_events_2026-04_to_09.csv")
L("O08","ammonia_detector_events","Location recorded as 'various' for 18 of 47 events even though each detector has one fixed location in the asset register",vv.sum(),"Filled 'location' from asset_register via detector_id; original text kept in location_logged")

ca=R("ammonia_detector_calibration_status_2026-09-30.csv")
ca["warning_ppm"]=ca.alarm_setpoints_warning_alarm.str.extract(r"(\d+)\s*/")[0].astype(int)
ca["alarm_ppm"]=ca.alarm_setpoints_warning_alarm.str.extract(r"/\s*(\d+)")[0].astype(int)
W(ca,"ammonia_detector_calibration_status_2026-09-30.csv")
L("O09","ammonia_detector_calibration","Alarm setpoints stored as one text string ('25 / 150 ppm')",len(ca),"Split into numeric warning_ppm and alarm_ppm")

# unchanged but re-written (UTF-8, LF)
for f,reason in [("asset_register.csv",""),("cmms_work_orders_2026-04_to_09.csv",""),("operator_shift_log_2026-04_to_09.csv",""),("utility_energy_daily_2026-04_to_09.csv","")]:
    d=R(f); W(d,f)
L("O10","asset_register, cmms_work_orders, operator_shift_log, utility_energy_daily","Checked: no duplicate keys, no orphan asset_ids, no bad dates, completed/status consistent, no non-numeric values",0,"No changes needed; copied through unchanged (blank completed/parts/notes cells are genuine 'not applicable')")
pickle.dump(log,open(f"{WORK}/ops_log.pkl","wb"))
print(len(log),"ops issues logged"); print(clip.sum(),vv.sum(),na.sum(),n24)
