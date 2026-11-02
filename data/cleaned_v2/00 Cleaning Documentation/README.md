# 00 Cleaning Documentation

| File | What it is |
|---|---|
| `cleaning_log.csv` | Every fix with the number of rows affected |
| `data_dictionary.csv` | Column meanings for every output file |
| `known_events_from_ops_records.csv` | Ground truth: 26 events (E01-E26) built from work orders, shift log, detectors and reviews, with what was checked in the controller data. This is the scoring set for detection |
| `review_claims_check.csv` | 309 numbers quoted in the six daily reviews, each compared with the raw controller data |
| `source_conflicts_and_review_errors.csv` | Places where the reviews, ops records, READMEs and controller data disagree, including two errors in the 2026-06-09 review |

Read `source_conflicts_and_review_errors.csv` before deciding which source wins in a disagreement.
