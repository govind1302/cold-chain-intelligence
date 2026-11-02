# 00_data_cleaning

Code that turns the original controller `.txt` exports and operations `.csv` files into the cleaned data in `data/cleaned_v2/`.

| File | What it does |
|---|---|
| `parse.py` | Parses both export layouts (June per-report files, Apr-May/Jul-Sep nightly fixed-width files) into point blocks |
| `build.py` | Cleans the controller data: names, units, duplicates, dead and stuck sensors, outage zeros, unavailable setpoints. Writes the per-plant CSVs |
| `ops.py` | Cleans the operations CSVs: merges months, fixes clipped door times, converts 24:00, fills detector locations |

## Run it

You only need this to rebuild or change the cleaned data. Put the unzipped original data under `data/raw/` (it is git-ignored), then:

```bash
cd 00_data_cleaning
export RAW_ROOT="../data/raw/S2-CON-1-Odyssey - Cold Chain Intelligence Data"
export WORK_DIR=_work            # scratch folder, git-ignored
export OUT_DIR=../data/cleaned_v2
python parse.py && python build.py && python ops.py
```

Rebuilding from the raw files reproduces the controller and operations CSVs in `data/cleaned_v2/` byte for byte.

## What is not regenerated

The files in `data/cleaned_v2/00 Cleaning Documentation/` (cleaning log, data dictionary, known events, review check, source conflicts) were written separately. If you change a cleaning rule, update `cleaning_log.csv` by hand.

## Rules

- Keep every raw value in `value_raw`. Blank `value_clean` only with a `quality_flag` that explains why.
- Never fill a gap with an old value.
- Describe any rule change in the pull request and in `cleaning_log.csv`.

## To do

- [ ] Add a script that regenerates `cleaning_log.csv`, so the documentation folder is reproducible too
- [ ] Add unit tests for the parser (both layouts, glued numbers, repeated page headers)
- [ ] Move the review-number check (`review_claims_check.csv`) into code
