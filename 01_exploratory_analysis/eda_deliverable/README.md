# eda_deliverable

EDA built on the team problem statement (guiding question + five sub-questions).

| File | What it is |
|---|---|
| `EDA_report.docx` / `EDA_report.pdf` | Section 1 raw-to-clean data, summary, project plan, analysis plan table (living, v1), descriptive statistics, seven findings with takeaways and plain-language explanations |
| `EDA_infographic.pdf` / `.png` | One-page infographic: stat tiles, raw-to-clean band, six visuals with call-outs, overall takeaway |
| `EDA graphs/` | The seven infographic graphs, one PNG each, named for what they show |
| `EDA.zip` | The report (Word and PDF), the infographic PDF and `EDA graphs/`, packaged together |
| `EDA_dashboard.pptx` | Earlier slide version. Not updated with the raw-to-clean section, the plain-language explanations or the 9,429 bad-reading count; the team is not using it |
| `figures/` | Figures (with and without titles) |
| `stats.json`, `descriptive_stats_by_point.csv`, `cold_rooms_over_41F.csv` | Every number used |
| `explanations.json` | The plain-language text shown beside each graph (shared by the report and the infographic) |

Counting rule used everywhere: 9,429 readings are lost to bad data (dead, stuck, outage zeros, impossible values). The 70,224 Plant B setpoint readings that were never exported are counted separately.

Rebuild from the repo root:

```bash
pip install -r requirements.txt
npm install -g docx
python 01_exploratory_analysis/eda_deliverable/eda_analysis.py
python 01_exploratory_analysis/eda_deliverable/make_infographic.py
NODE_PATH=$(npm root -g) node 01_exploratory_analysis/eda_deliverable/make_report.js
```
