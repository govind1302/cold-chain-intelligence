# evaluation

How every model is scored. The ground truth is `data/cleaned_v2/00 Cleaning Documentation/known_events_from_ops_records.csv` (26 events).

## Metrics

| Metric | Target (PRD) |
|---|---|
| Share of seeded or known faults detected | 80 percent or more |
| Time to detect (days after onset), especially for slow faults | Slow faults caught by day two |
| Unexplained High and Critical alerts per plant per week | 2 or fewer |
| Alerts from dead sensors, outages, planned maintenance | None |
| Forecast error versus "same hour yesterday" | At least 15 percent better, with big misses explained |

## Protocol

1. Train only on Apr-May. Fix parameters before looking at the test period.
2. Run on June and on Jul-Sep. Merge repeats into episodes first, or the alert rate is meaningless.
3. For each known event record: first alert time, rule, priority, days after onset.
4. Negative controls must produce no alert: UC-25 stuck (8/4-8/10), controller outage (Plant A 9/15), power blip (Plant B 8/19), firmware update (Plant B 8/31), lead/lag swaps.
5. Classify every other High or Critical episode as explained (by a schedule, a door, a work order or a chronic condition) or unexplained, and report the unexplained rate per week.

## Cautions

- Operations records are labels. Never use them as inputs for detection.
- If you tune after seeing a test period, say so and treat the result as development, not a held-out test.
- June is real but only 8 days, and it is warmer than the simulated training months.

## To do

- [ ] One shared scoring module that works for all three plants (today `plant_a/score_plant_a.py` is Plant A only)
- [ ] A results table saved to this folder after every run
