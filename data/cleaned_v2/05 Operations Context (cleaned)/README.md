# 05 Operations Context (cleaned)

Plant records around the refrigeration data. They cover Apr-May and Jul-Sep only (the work orders have a single June row). All times are plant local.

## Labels and scoring (do not use as model inputs)

| File | What it is |
|---|---|
| `cmms_work_orders_2026-04_to_09.csv` | Preventive and corrective maintenance, with notes on what was found |
| `operator_shift_log_2026-04_to_09.csv` | Free-text shift notes. The timestamps are unreliable; use the text and the date |
| `controller_alarm_history_2026-04_to_09.csv` | Controller alarms, with `acknowledged`, `duration_min` and parsed thresholds |
| `ammonia_detector_events_2026-04_to_09.csv` | Detector readings above background, all below alarm |
| `field_rounds_handheld_2026-04_to_09.csv` | Twice-daily manual readings with an explicit `unit` column |

## Context features (usable by models)

| File | What it is |
|---|---|
| `production_and_sanitation_schedule_2026-04_to_09.csv` | Production, sanitation and holidays, with real `start_ts` and `end_ts` |
| `dock_door_events_2026-04_to_09.csv` | Every dock door open and close (five months merged). Closed times recomputed where clipped at 23:59 |
| `receiving_log_2026-04_to_09.csv` | Inbound receipts. `temp_applicable` is False for dry goods and packaging |
| `weather_service_hourly_2026-04_to_09.csv` | Outdoor temperature for each plant (`plant` column added) |
| `utility_energy_daily_2026-04_to_09.csv` | Daily kWh and peak kW per plant |

## Reference

| File | What it is |
|---|---|
| `asset_register.csv` | Equipment list. Use `serves` to link dock doors to rooms |
| `ammonia_detector_calibration_status_2026-09-30.csv` | Calibration and bump-test status. Plant B detectors were overdue from 2026-08-29 |
