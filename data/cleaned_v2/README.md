# cleaned_v2

Cleaned data, version 2. Start with `START_HERE_analysis_plan.txt`, then `README_cleaning_notes.txt`.

| Item | What it is |
|---|---|
| [`Controller Data (cleaned)/`](Controller%20Data%20%28cleaned%29/README.md) | Tidy hourly readings, daily summaries, point inventory and coverage for each plant |
| [`05 Operations Context (cleaned)/`](05%20Operations%20Context%20%28cleaned%29/README.md) | Work orders, shift log, alarms, detectors, dock doors, receiving, schedule, weather, energy |
| [`00 Cleaning Documentation/`](00%20Cleaning%20Documentation/README.md) | Cleaning log, data dictionary, known events, review check, source conflicts |
| `START_HERE_analysis_plan.txt` | Suggested order of work |
| `README_cleaning_notes.txt` | What was fixed, what was deliberately left alone |

## The one rule

Every controller value keeps its original in `value_raw`. `value_clean` is blank only where `quality_flag` says why. Flags: `sensor_disconnected`, `export_truncated_zero_fill`, `implausible_value`, `stuck_value`, `setpoint_unavailable`.
