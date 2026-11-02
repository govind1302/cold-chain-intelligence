# Plant C

One report: Temperature Report (rooms, freezers and ambient air). There are no setpoints and no pressures or compressor data.

| File | Rows |
|---|---|
| `PlantC_hourly_long.csv` | 73,440 |
| `PlantC_daily_summary.csv` | one row per point per day |
| `PlantC_point_inventory.csv` | 20 points |
| `PlantC_coverage.csv` | every date from 2026-04-01 to 2026-09-30 |

Things to know:
- Normal has to be learned from history (no setpoints).
- Back Dock Temp drifts to 130-283 F on 2026-05-20 to 06-04 and 2026-09-03 to 09-12 (sensor fault, confirmed by work orders). Hourly values above 130 F are blank with flag `implausible_value`. Lower drifting values are kept.
- Missing days: 04-18, 05-03, 07-12, 08-02, 08-30, 09-27. June has 6 real days.
- Known conditions: Protein Room Front chronically warm until 2026-08-05, Queso Cup Chiller about 10 F warm from late June to 07-22, Freezer slowly warming in Aug-Sep.
