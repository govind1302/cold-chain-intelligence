# 01_exploratory_analysis

Goal: understand the data well enough to choose points, features and thresholds for the models, and to write down what is normal at each plant.

Inputs: everything in `data/cleaned_v2/`. Read `docs/START_HERE_analysis_plan.txt` and the source conflicts file first.

| Folder | What goes there |
|---|---|
| [`notebooks/`](notebooks/README.md) | Jupyter notebooks, one per question |
| [`figures/`](figures/README.md) | Saved charts used in findings |
| [`findings/`](findings/README.md) | One short written finding per question |

## Task checklist

Work in this order. Tick the box when the finding is written in `findings/`.

- [ ] 1. Coverage: how much is missing or flagged, per plant and month (`*_coverage.csv`, `cleaning_log.csv`)
- [ ] 2. Point inventory: pick about 15 points per plant that matter (rooms, freezers, receiver, engine room, discharge pressure, compressors). Drop setpoints, counters and idle channels
- [ ] 3. Hour-of-day profiles per point from `value_clean`, by weekday and weekend
- [ ] 4. Regimes: spiral freezers on and off (Plant B), compressor lead and lag weeks (Plant B), production and sanitation windows
- [ ] 5. Which points move together (correlation, PCA): shared evaporators and defrost groups
- [ ] 6. Daily summary lines versus hourly values: how many transients does the hourly data miss?
- [ ] 7. Overlay operations records on the profiles and reproduce events E03, E06, E10, E21, E23 and E25 by eye
- [ ] 8. Dock doors and receiving: do long door-open times line up with warm coolers (start with Plant A door D4)?
- [ ] 9. Weather and energy: does outdoor temperature explain engine-room and condenser behavior?
- [ ] 10. Detectors: are sub-alarm readings trending up (start with detector GD-A-04)? Compare with calibration status
- [ ] 11. Alarm history: how many alarms had a real excursion behind them? Why are 83 unacknowledged?
- [ ] 12. Chronic conditions the baseline would learn as normal (for example Plant A Pre-Weigh at about 42 F)

## Rules for this folder

- Use `value_clean` and rows where `quality_flag` is blank. Never fill gaps.
- Treat June as real and the other months as simulated. Do not mix them in one baseline without saying so.
- The operations records are labels, not features. Use them to explain what you see, not to predict it.
- Name notebooks `NN_topic_initials.ipynb` and keep each to one question.
- Every chart saved to `figures/` must be referenced from a finding.

## Done when

All 12 boxes are ticked and the findings give, per plant, the list of modeled points, the regimes to condition on, and the traps to avoid. Hand that list to `02_modeling/`.

## Traps (see also the plan in `docs/`)

- 459.6 is a dead sensor. Zeros after a controller outage are missing data, not a cold room.
- A temperature that is flat for a whole day is a stuck sensor, not a healthy room.
- Idle compressors and lead/lag swaps look odd but are normal.
- Hot engine room in a heat wave is weather; hot when it is cooling off outside is a fault.
