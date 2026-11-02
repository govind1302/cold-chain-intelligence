# data

All data used by the project. Nothing in here is edited by hand.

| Folder | Contents |
|---|---|
| [`cleaned_v2/`](cleaned_v2/README.md) | The cleaned dataset (version 2): controller data per plant, operations records, and the cleaning documentation |
| `raw/` | Not in git. Put the original zip contents here if you need to rebuild the cleaned data (see `00_data_cleaning/`) |

## Provenance

`cleaned_v2/` was produced from `S2-CON-1-Odyssey - Cold Chain Intelligence Data.zip` by the code in `00_data_cleaning/`. Rebuilding from the raw files gives byte-identical output for the controller and operations CSVs. The documentation files in `cleaned_v2/00 Cleaning Documentation/` were written separately and are maintained by hand.

## Real versus simulated

| Period | Controller data | Operations records |
|---|---|---|
| Apr-May 2026 | Simulated | Present |
| June 2026 | Real (8 days for A and B, 6 for C) | Almost none (one work order) |
| Jul-Sep 2026 | Simulated | Present |

## Size

About 154 MB in total. The largest files are `PlantB_hourly_long.csv` (79 MB) and `PlantA_hourly_long.csv` (51 MB). GitHub warns above 50 MB and rejects above 100 MB.

## Rules

- Raw data stays out of git.
- To change the data, change the cleaning code, regenerate, and describe the change in the pull request and in `cleaning_log.csv`.
- Do not try to identify the company.
