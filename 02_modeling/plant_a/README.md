# plant_a

Working baseline for Plant A, plus its scoring.

| File | What it does |
|---|---|
| `plant_a_baseline.py` | Builds normals, applies the rules, drift and engine-room models, merges repeats into episodes |
| `score_plant_a.py` | Scores the episodes against the known events, runs negative controls, counts unexplained alerts and checks the schedule and dock joins |
| `outputs/` | Generated results ([README](outputs/README.md)) |

## Run

```bash
python 02_modeling/plant_a/plant_a_baseline.py      # writes outputs/plant_a_baseline_events.csv
python 02_modeling/plant_a/score_plant_a.py         # prints the scorecard
```

Both default to `data/cleaned_v2`. Pass another folder as the first argument if needed.

## Steps in the code

1. Load clean rows from the System Monitor report, pivot to one column per point (gaps stay blank).
2. Learn normals: median and MAD by hour of day and weekday or weekend, trained before 2026-06-01.
3. Flag points: robust z above 3.5 for two hours in a row.
4. Food-safety rule: a cold room above 41 F for 2+ hours is High.
5. Plant-wide event: 3+ points deviating together. High only if 2+ cold rooms exceed 41 F, otherwise Medium.
6. Critical rule: receiver level at or below 1% for 2+ hours during production.
7. Slow drift: EWMA on daily residuals and a Theil-Sen trend over 28 days.
8. Engine room: Huber regression on ambient and discharge pressure; one day 10 F or more above expected is High.
9. Merge repeats within 3 days into one episode.

## Latest scorecard

See the table in `../README.md`. Negative controls pass: no alert on the stuck UC-25 sensor, none caused by the 9/15 outage. Unexplained High alerts in Jul-Sep: 10 episodes (0.77 per week), all UC-7 inside the scheduled washdown window. All 8 UC-9/10 days above 41 F after July 1 follow a Carrier K unload at door D4.

## Known limits

- Hourly data cannot resolve 30 minutes; short spikes need the daily summary lines.
- With nightly exports, even Critical is next-morning at best.
- June has only 8 days, and the simulated training months do not match real June.
- Rules were adjusted after the first run, so Jul-Sep is not a clean test.

## To do

- [ ] Schedule suppression for washdown
- [ ] Use the daily summary High and Low times for short transients
- [ ] Add the Valve Group setpoints for a setpoint-relative score
- [ ] Add a plain-language explanation to each episode
