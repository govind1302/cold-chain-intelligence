import re, os, glob, json
import pandas as pd
from collections import Counter

ROOT = os.environ.get("RAW_ROOT", "raw/S2-CON-1-Odyssey - Cold Chain Intelligence Data")   # unzipped original data
WORK = os.environ.get("WORK_DIR", "_work")                                                    # scratch folder (git-ignored)
os.makedirs(WORK, exist_ok=True)
HDR_RE = re.compile(r"Refrigeration Controller User Defined Report\.\s+(.*?) - (Plant [ABC])\s+(\d\d)-(\d\d)-(\d{4})")
REP_RE = re.compile(r"^(.*?)\s*-\s*Analog Information Report For\s+(\d+)-\s*(\d+)-(\d{4})")
SUM_RE = re.compile(r"High =\s*(\S+)\s+at\s+(\d\d:\d\d)\s+Low =\s*(\S+)\s+at\s+(\d\d:\d\d)\s+Average =\s*(\S+)")
NUM = r"-?\d+\.\d+"

def parse_file(path, source_folder):
    issues = []
    with open(path, encoding="utf-8", errors="replace", newline=None) as fh:
        lines = fh.read().split("\n")
    fname = os.path.basename(path)
    plant_fn = re.match(r"Plant([ABC])_(\d{4}-\d\d-\d\d)", fname)
    plant = "Plant " + plant_fn.group(1); file_date = plant_fn.group(2)
    company=None; hdr_date=None; report=None; rep_date=None
    rows=[]; summ=[]
    i=0; n=len(lines); page=0; block_idx=0
    while i<n:
        ln=lines[i]
        m=HDR_RE.search(ln)
        if m:
            hdr_date=f"{m.group(5)}-{m.group(3)}-{m.group(4)}"; page+=1; i+=1; continue
        m=REP_RE.match(ln.strip())
        if m:
            report=m.group(1).strip(); rep_date=f"{int(m.group(4)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"; i+=1; continue
        s=ln.strip()
        if (not s) or s.startswith("Description") or s.startswith("00 ") or s.startswith("===="):
            i+=1; continue
        # point block: name line, values line, summary line
        if i+2<n and SUM_RE.search(lines[i+2]):
            name=s; vline=lines[i+1]
            mm=re.match(r"^\s*((?:-?\d+\.\d+\s*)*)(.*)$", vline)
            vals=mm.group(1).split(); unit=mm.group(2).strip() or None
            # handle glued numbers e.g. 12.3-4.5
            vals2=[]
            for t in vals:
                if re.fullmatch(NUM,t): vals2.append(t)
                else:
                    parts=re.findall(NUM,t)
                    if parts and "".join(parts)==t: vals2.extend(parts); issues.append((fname,name,"glued_tokens",t))
                    else: vals2.append(t); issues.append((fname,name,"bad_token",t))
            if len(vals2)!=24: issues.append((fname,name,"n_values_%d"%len(vals2),vline[:80]))
            sm=SUM_RE.search(lines[i+2]).groups()
            block_idx+=1
            rows.append(dict(source_file=fname,source_folder=source_folder,plant=plant,file_date=file_date,header_date=hdr_date,
                report_date=rep_date,report=report,page=page,block=block_idx,point=name,unit=unit,values=vals2,
                high=sm[0],high_time=sm[1],low=sm[2],low_time=sm[3],avg=sm[4]))
            i+=3; continue
        issues.append((fname,None,"unparsed_line",s[:100])); i+=1
    return rows, issues

def all_files():
    out=[]
    for sub,tag in [("01 Raw Controller Exports","01_raw_june"),("04 Extended History (Apr-May & Jul-Sep 2026)","04_extended")]:
        for p in sorted(glob.glob(f"{ROOT}/{sub}/Plant */*.txt")): out.append((p,tag))
    return out

if __name__=="__main__":
    allrows=[]; allissues=[]
    for p,tag in all_files():
        r,iss=parse_file(p,tag); allrows+=r; allissues+=iss
    import pickle; pickle.dump((allrows,allissues),open(f"{WORK}/parsed.pkl","wb"))
    print(len(allrows),"blocks;",len(allissues),"issues")
    print(Counter(i[2] for i in allissues).most_common(20))
    for i in allissues[:25]: print(i)
