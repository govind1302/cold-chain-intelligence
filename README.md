# Cold Chain Intelligence

Monitoring and alerting for ammonia refrigeration at three plants (Plant A, Plant B, Plant C) of a prepared-foods manufacturer. In the project the company is called Harbor Table Foods.

Client: Contextual IO. Team: SEC02_Contextual_Odyssey.

The goal (from the PRD): read the nightly controller exports, find real faults early, separate them from sensor errors and normal operations, explain likely causes, rate severity (Low / Medium / High / Critical), notify the right person for High and Critical, and make everything traceable to the source readings. The system advises people. It never controls equipment.

> Confidentiality: the data is anonymized. Do not try to identify the source company. Keep this repository private.

## Repository map

| Folder | What it is | Start with |
|---|---|---|
| [`data/`](data/README.md) | Cleaned data (v2) used by everything else | `data/cleaned_v2/START_HERE_analysis_plan.txt` |
| [`00_data_cleaning/`](00_data_cleaning/README.md) | Code that turns the raw exports into the cleaned data | `README.md` |
| [`01_exploratory_analysis/`](01_exploratory_analysis/README.md) | Notebooks, figures and findings | The task checklist in its `README.md` |
| [`02_modeling/`](02_modeling/README.md) | Baseline detection models and scoring | `plant_a/` (working baseline) |
| [`03_frontend_design/`](03_frontend_design/README.md) | Requirements, wireframes and design system for the web app | `requirements/frontend_requirements.md` |
| [`docs/`](docs/README.md) | PRD, one-pager, web app requirements, original source READMEs | `webapp_requirements_and_system_design.md` |

Every folder has its own `README.md` saying what belongs there and what to do next.

## Quick start

```bash
git clone <repo-url>
cd cold-chain-intelligence
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# run the Plant A baseline and score it against the known events
python 02_modeling/plant_a/plant_a_baseline.py
python 02_modeling/plant_a/score_plant_a.py
```

Load the cleaned data in a notebook:

```python
import pandas as pd
hourly = pd.read_csv("data/cleaned_v2/Controller Data (cleaned)/Plant A/PlantA_hourly_long.csv",
                     low_memory=False, keep_default_na=False, na_values=[""])
good = hourly[hourly.quality_flag.isna()]          # rows with a clean value_clean
```

## What you need to know about the data

- June 2026 controller data is real: 8 days for Plants A and B, 6 days for Plant C.
- Apr-May and Jul-Sep controller data is simulated, and the operations records (work orders, shift log, alarms, detectors, dock, receiving, schedule, weather, energy) cover only those simulated months.
- Plant B setpoints are only real from 2026-06-10. Plant C has no setpoints. Plant A has them.
- The operations records are labels for scoring, not model inputs. Using them as inputs would inflate results.
- The reviews, ops records and controller data disagree in a few places. Read `data/cleaned_v2/00 Cleaning Documentation/source_conflicts_and_review_errors.csv` before you decide which source wins.

## Status

| Area | Status |
|---|---|
| Parser and cleaning (v2), review number check | Done |
| Ground-truth event map (26 events) | Done |
| Plant A baseline detection | Working, scored (see `02_modeling/plant_a/`) |
| Exploratory analysis | Not started |
| Plant B and Plant C baselines | Not started |
| Forecasting, daily review writer | Not started |
| Web app requirements and front-end requirements | Drafted |
| Wireframes and design system | Not started |

## How we work

- Never edit files in `data/cleaned_v2/` by hand. Change the code in `00_data_cleaning/` and regenerate, so the data stays reproducible.
- Branch per task (`eda/coverage`, `model/plant-b`, `design/alert-detail`), open a pull request, get one review.
- Notebook names: `NN_topic_initials.ipynb` (for example `03_hour_of_day_profiles_ab.ipynb`). Clear outputs before committing large notebooks.
- Figures go in `01_exploratory_analysis/figures/`, written findings in `01_exploratory_analysis/findings/`.
- Large files: the biggest data file is about 79 MB. Do not commit anything larger than 50 MB without checking with the team.
- Keep changes small and say in the pull request which README task you are closing.

## Delivery plan (from the PRD)

| Week | Phase | Done when |
|---|---|---|
| 1 | Ingest and inventory | Nightly files readable without cleanup (done) |
| 2 | Data quality and baselines | Sensor faults separated from real data (cleaning done, baselines in progress) |
| 3 | Detection and context | Real faults separated from normal activity |
| 4 | Reporting and alerts | Automatic reviews, right person alerted |
| 5 | Validation and handover | Success criteria met, final demo |
