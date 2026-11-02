# Plant B

Reports: Area Temperatures and Vessels, Compressor 1 to 4 Readings, Valve Group Report with Setpoints.

| File | Rows |
|---|---|
| `PlantB_hourly_long.csv` | 384,336 |
| `PlantB_daily_summary.csv` | one row per point per day per report |
| `PlantB_point_inventory.csv` | 85 points |
| `PlantB_coverage.csv` | every date from 2026-04-01 to 2026-09-30 |

Things to know:
- Setpoints read 0.0 (never exported) everywhere except from 2026-06-10 onward. Rows without a real setpoint are blank in `value_clean` with flag `setpoint_unavailable`. Of the 19 setpoints, 14 held one value on all four real days (June 10, 25, 28, 30) and 5 took more than one value: UC-3 and UC-4 Filling Room, UC-5 Packing, UC-6 and UC-7 Boxing and Dock.
- Dead sensors read 459.6 (summary -459.67): UC-7 Boxing and Dock on almost every day (live on 06-28 and 06-30 only), UC-4 Filling Room from 06-25 to 07-08. Flag `sensor_disconnected`.
- Files named 2026-06-05 contain data for 2026-06-04 (`date_corrected = True`).
- C-1 and C-2 swap lead and lag each week, so idle-compressor values look odd but are normal. C-3 is the booster that always runs; C-4 is standby.
- Missing: no files on 2026-08-20; compressor reports missing on 04-22, 07-16, 08-27, 09-10.
- 2026-08-19 14:05 utility power interruption: compressor loads are 0 in hour 15.
