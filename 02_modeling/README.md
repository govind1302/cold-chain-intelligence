# 02_modeling

Goal: detect real faults early, separate them from sensor errors and normal operation, explain and rate them. Start simple and explainable. The PRD says: begin with a rolling median and spread by hour, grow only where needed.

| Folder | What it is |
|---|---|
| [`plant_a/`](plant_a/README.md) | Working baseline for Plant A, scored |
| [`plant_b/`](plant_b/README.md) | Plan for Plant B (compressor regimes, dead sensors) |
| [`plant_c/`](plant_c/README.md) | Plan for Plant C (no setpoints) |
| [`evaluation/`](evaluation/README.md) | How we score every model |

## Approach

| Problem | Method |
|---|---|
| Bad data (dead, stuck, outage, gaps) | Rules, already done in cleaning |
| Normal range per point | Robust median and MAD by hour of day and weekday or weekend, trained on Apr-May |
| Food-safety breach | Rule: cold room above 41 F for 2+ hours (hourly data cannot see 30 minutes) |
| Many rooms at once | Count points deviating together; High only if 2+ rooms exceed 41 F |
| Receiver at 0% in production | Rule: level at or below 1% for 2+ hours between 06:00 and 22:00 is Critical |
| Slow drift | EWMA on daily residuals and a Theil-Sen trend over 28 days |
| Weather confounding | Huber regression of engine-room temperature on ambient and discharge pressure |
| Repeats | Merge the same rule and point within 3 days into one episode |
| Known causes | Joins to the sanitation schedule, dock events, work orders |

Not now: LSTMs, autoencoders, supervised event classifiers (too little data and too few labels, and they are hard to explain).

## Data split

Train on Apr-May (simulated). Validate on June (real, 8 days). Test on Jul-Sep (simulated). Only `value_clean` rows are used.

## Results so far (Plant A, development run)

| Event | First alert | Priority | Days after onset |
|---|---|---|---|
| E01 Receiver at 0% (6/9) | 6/9 09:00 | Critical | 0 |
| E03 02:45 freezer spike growing | 6/4 | Low | 3 |
| E04 Spike returns in Sept | 9/17 | Low | 10 |
| E05 Engine room 102 F (6/30) | 6/30 | High | 0 |
| E06 EF-2 fan failing | 8/13 | Medium | 4 |
| E09 Door D4 seal, Carrier K unloads | 7/14 | High | 8.5 |
| E10 Receiver level slowly falling | 8/1 | Low | 0 |
| E11 Chronic Pre-Weigh above 41 F | 4/1 | High | 0 |

Read these with care: rules were adjusted after the first run, so Jul-Sep is a development result and not a clean held-out test. June is warmer than the simulated training months, so June episode counts are not a false-alarm rate.

## Next steps

- [ ] Plant B baseline (see `plant_b/README.md`)
- [ ] Plant C baseline (see `plant_c/README.md`)
- [ ] Suppress alerts inside the scheduled sanitation window unless the reading is worse than the learned washdown normal (removes all 10 unexplained Plant A alerts in Jul-Sep)
- [ ] Add dock-door joins as a feature or an explanation (Plant A door D4 and Carrier K)
- [ ] Combine receiver level, detector rate and shift-log keywords into one slow-leak score (E10)
- [ ] Severity score and priority mapping (Low, Medium, High, Critical) from rules
- [ ] Daily forecast baseline: same hour yesterday, then a model that beats it by 15 percent
- [ ] Re-score everything on a truly held-out period or on data from the client

## Rules

- Parameters are chosen before looking at the test period. Say so if you change them afterwards.
- Never use work orders, shift logs, alarms or detector events as model inputs for detection. They are labels.
- Never fill gaps. A missing reading is missing.
- Every alert must come with a plain-language reason and the evidence readings.
