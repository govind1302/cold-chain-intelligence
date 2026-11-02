COLD CHAIN INTELLIGENCE - CLEANED DATA (v2)
===========================================
Source: S2-CON-1-Odyssey - Cold Chain Intelligence Data.zip. Every file in the zip was read:
511 controller .txt exports, 20 ops .csv files, the 6 daily reviews, the 4 OEE files, both
READMEs, the Launchpad one-pager and the PRD. Only .txt/.csv data is included here.

PRINCIPLE: nothing is deleted or silently overwritten.
Every controller value keeps its original in value_raw; value_clean is blank only where a
quality_flag explains why. Real events (06-09 receiver and oil leak, the 02:45 QFM spikes,
06-30 engine room, etc.) are untouched.

FOLDER LAYOUT
  Controller Data (cleaned)/
     Plant A/  Plant B/  Plant C/
        Plant?_hourly_long.csv     tidy: one row per plant/hour/report/point
        Plant?_daily_summary.csv   the controller's High/Low/Average lines, cleaned
        Plant?_point_inventory.csv one row per point
        Plant?_coverage.csv        which dates/report groups exist and which are missing
  05 Operations Context (cleaned)/  the 12 ops CSVs (dock events and weather merged across months)
  00 Cleaning Documentation/
        cleaning_log.csv                        every fix with row counts
        data_dictionary.csv                     column meanings
        known_events_from_ops_records.csv       26 ground-truth events with what was verified in the data
        review_claims_check.csv                 309 numbers from the six reviews checked against raw data
        source_conflicts_and_review_errors.csv  places where sources disagree (incl. 2 review errors)
  START_HERE_analysis_plan.txt      what to do first, and why

WHAT WAS FIXED (see cleaning_log.csv)
  Controller txt -> csv in one schema; whitespace in point names; 7 unit spellings -> 7 standard
  units; 474 duplicate blocks dropped; 8,064 disconnected-sensor readings (459.6) blanked; Plant A
  2026-09-15 hours 14-23 zero-fill blanked (confirmed by WO-26501: data not recorded); Plant C Back
  Dock readings >130 F blanked (confirmed by WO-26510/26511); Plant A UC-25 7-day stuck sensor
  flagged (confirmed by WO-26500); Plant B setpoints never exported blanked; Plant B files named
  06-05 re-dated to 06-04; setpoints linked to measured points.
  Ops: dock-door close times clipped at 23:59 recomputed; 24:00 end times converted;
  '(not acknowledged)' -> boolean; 'various' detector locations filled from the asset register;
  units made explicit in field rounds; monthly files merged.

IMPORTANT: WHAT KIND OF DATA EACH PART IS
  * June 2026 controller data is REAL (8 days for Plants A and B, 6 for Plant C).
  * Apr-May and Jul-Sep controller data is SIMULATED, and the ops CSVs (work orders, shift log,
    alarms, detectors, field rounds, dock, receiving, schedule, weather, energy) cover only those
    simulated months (the CMMS has a single June row). The ops records therefore explain the
    simulated faults, not the real June events.
  * The seams do not always agree (see source_conflicts_and_review_errors.csv SC04-SC06).

WHAT WAS DELIBERATELY NOT CHANGED
  * Missing days / report groups are NOT imputed (see *_coverage.csv).
  * Plant C Back Dock drift below 130 F (the sensor ramps before it goes impossible).
  * Controller summary lines still differ from hourly values by design.
  * Idle compressors and transfer counters flat-line legitimately and are kept.
  * Slightly negative suction pressures (vacuum) are plausible and kept.
  * The same point in two reports (e.g. Plant A UC-1 Engine Room); both kept, filter by report.
  * Cleaned .txt files were not produced: CSV is more useful for modeling.
