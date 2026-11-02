# README 2: Extended History and Operations Context

This adds to the original README. Two new folders give you about five months of plant history and the operational records that real plants keep around their refrigeration data.

## 04 Extended History (Apr–May and Jul–Sep 2026)

- **Coverage:** nightly controller exports for 1 Apr – 31 May and 1 Jul – 30 Sep 2026, one file per plant per day: Plant{A|B|C}_{YYYY-MM-DD}_nightly-export.txt. June is covered by the real sample files in folder 01.

- **Origin:** this history was simulated from the behavior of the real plants, so treat it like real plant data. It has the same point names, units and report groups.

- **Format:** each file holds all of that plant's report groups back to back, in the controller's original fixed-width layout. That differs from folder 01, where each file is one report with normalized spacing. Your parser needs to handle both.

- Plant A: System Monitor Points, then Valve Group Report w/Setpoints.

- Plant B: Area Temperatures And Vessels, Compressor 1–4, then Valve Group Report w/Setpoints.

- Plant C: Temperature Report.

- **Completeness:** expect what you'd get from a real site. Some days are missing files, some files are missing a report group, and not every value is trustworthy.

## 05 Operations Context

| **File** | **What it is** | **Key columns** |
| --- | --- | --- |
| asset_register.csv | Equipment list for all three plants: compressors, condensers, vessels, evaporators, doors, ammonia detectors, controllers | asset_id, plant, asset_type, location, serves, pm_program |
| cmms_work_orders_2026-04_to_09.csv | Maintenance system export, preventive (PM) and corrective (CM) | wo_id, asset_id, wo_type, priority, opened, completed, status, description, notes |
| operator_shift_log_2026-04_to_09.csv | Free-text shift log written by operators and techs | timestamp, plant, shift, author_role, entry |
| field_rounds_handheld_2026-04_to_09.csv | Twice-daily manual readings with handheld thermometers, sight glasses and panel gauges | timestamp, plant, round, point, instrument, reading, note |
| controller_alarm_history_2026-04_to_09.csv | Alarms raised by the controllers, and who acknowledged them | alarm_start, alarm_clear, point, alarm, peak_value, acknowledged_by |
| dock_door_events_2026-MM.csv | Every dock door open/close, by month | door, door_function, opened, closed, open_minutes, direction, carrier, receipt_id |
| receiving_log_2026-04_to_09.csv | Inbound receipts, joined to dock events by receipt_id | supplier, category, pallets, reefer_setpoint_F, product_temp_at_receipt_F, disposition |
| production_and_sanitation_schedule_2026-04_to_09.csv | When each plant ran production and sanitation, plus holidays | date, plant, activity, start, end |
| weather_service_hourly_2026-MM.csv | Outdoor temperature, humidity and sky from a weather station near each plant | timestamp_local, station, temp_F, rel_humidity_pct, sky |
| ammonia_detector_events_2026-04_to_09.csv | Every logged ammonia detector reading above background, including readings below alarm | detector_id, location, duration_min, peak_ppm, level |
| ammonia_detector_calibration_status_2026-09-30.csv | Calibration and bump-test status per detector as of Sep 30 | last_calibration, calibration_due, last_bump_test |
| utility_energy_daily_2026-04_to_09.csv | Daily electricity use per plant | kwh, peak_kw, cooling_degree_days_F, scheduled_production_hours |

## Notes

- **Names:** suppliers and carriers are anonymized (Supplier 01, Carrier K). People appear only by role.

- **Doors near rooms:** the asset register's serves column says which rooms each dock door sits next to.

- **Compressors:** Plant B's high-stage compressors C-1 and C-2 swap lead and lag weekly. C-3 is the booster that runs all the time; C-4 is a standby booster.

- **Local time:** all timestamps are plant local time.

## Your challenge

Somewhere in these five months, things went wrong. Some were sudden, some built up slowly over weeks, and some only show up when you combine sources.

Build a system that finds them on its own, explains each one, judges how serious it is, and says who should be told. Also make it tell real problems apart from things that only look like problems.