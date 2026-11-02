# plant_b

Not started. Plan for the Plant B baseline.

## What makes Plant B different

- Compressor reports (C-1 to C-4) and vessels, not just room temperatures.
- C-1 and C-2 swap lead and lag every week, so idle machines read 0% load and unusual oil, suction and discharge values. These are normal and must not alert.
- C-3 is the booster that always runs. C-4 is standby.
- Spiral freezers sit warm when off and pull down to -30 F or lower at startup (regime changes).
- Setpoints are real only from 2026-06-10; use learned normals.
- Dead sensors: UC-7 Boxing and Dock (almost always) and UC-4 Filling Room (06-25 to 07-08). They are blank in `value_clean`.
- Files are missing on 2026-08-20, and compressor reports on four more days.

## Events to find (see `data/cleaned_v2/00 Cleaning Documentation/known_events_from_ops_records.csv`)

E02 (C-1 oil leak, June 9), E12, E13 (dead sensors, suppress), E14 (power blip 8/19, explained), E15 (firmware update, suppress), E16 (C-1 oil top-ups), E17 (SF-1 slow pull-down in Sept), E18 (C-3 rougher, weak signal), E19 (lead/lag swap, must not alert), E20 (detector calibration overdue).

## Plan

- [ ] Label each compressor-week as lead, lag or standby from the loads, and learn normals per state
- [ ] Learn spiral freezer normals separately for off, pull-down and running
- [ ] Reuse the Plant A pipeline (normals, rules, drift) with those states
- [ ] Add engine room versus weather and load
- [ ] Join the schedule (production and sanitation) and work orders for suppression
- [ ] Score with `../evaluation/`

## Watch out

The weekly lead/lag swap makes C-1 oil pump pressure alternate between about 150 and 60 psig. Compare only like with like.
