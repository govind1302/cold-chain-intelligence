# Controller Data (cleaned)

Nightly controller exports (June real, Apr-May and Jul-Sep simulated) parsed into one schema, one folder per plant.

| Plant | Hourly rows | Points | Setpoints |
|---|---|---|---|
| Plant A | 257,664 | 50 | Yes |
| Plant B | 384,336 | 85 | Only from 2026-06-10 |
| Plant C | 73,440 | 20 | None |

Each plant folder has four files:

| File | Use it for |
|---|---|
| `Plant?_hourly_long.csv` | The main modeling table: one row per plant, hour, report and point |
| `Plant?_daily_summary.csv` | The controller's own High, Low and Average lines. The only place short transients (such as the 02:45 spike) are visible |
| `Plant?_point_inventory.csv` | One row per point: units, date range, share of hours flagged, normal range |
| `Plant?_coverage.csv` | Which dates and report groups exist, and which are missing and why |

Column meanings are in `../00 Cleaning Documentation/data_dictionary.csv`.

Use `value_clean` and rows where `quality_flag` is blank. Do not fill gaps.
