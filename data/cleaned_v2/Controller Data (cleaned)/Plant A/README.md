# Plant A

Reports: System Monitor Points and Valve Group Report with Setpoints. Some points (for example UC-1 Engine Room) appear in both, so filter on `report`.

| File | Rows |
|---|---|
| `PlantA_hourly_long.csv` | 257,664 |
| `PlantA_daily_summary.csv` | one row per point per day per report |
| `PlantA_point_inventory.csv` | 50 points |
| `PlantA_coverage.csv` | every date from 2026-04-01 to 2026-09-30 |

Things to know:
- Setpoints exist (rows with `is_setpoint = True`, linked through `measures_point`). UF-3 and UF-4 QFM setpoints changed from 18 to 10 F on 2026-06-04.
- 2026-09-15, hours 14-23, are blank in `value_clean` (controller lost communication, flag `export_truncated_zero_fill`).
- UC-25 is blank on 2026-08-04 to 08-10 (stuck sensor, flag `stuck_value`).
- Missing days: 2026-05-09 and 2026-09-21. The Valve Group report is also missing on 05-14 and 08-06.
- UC-27 RET Packout (System Monitor) and UC-28 RET Packout (Valve Group) are probably different points. They were kept as exported.
- Known chronic condition: UC-3/4 Pre-Weigh runs about 42 F against a 35 F setpoint in every month.
