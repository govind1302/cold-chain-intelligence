# Cold Chain Intelligence: Student Sample Data

Northeastern × Contextual semester project. Anonymized sample data from a real mid-market prepared-foods manufacturer with ammonia (NH3) refrigeration at three plants. In the project, the company is called **Harbor Table Foods**.

## What's in this folder

| **Folder** | **Contents** | **Files** |
| --- | --- | --- |
| 01 Raw Controller Exports | Nightly text exports from each plant's refrigeration controller, June 2026 | 61 .txt files |
| 02 Daily Ammonia System Reviews | The daily review written from those exports. This is the report your system should produce. | 6 Google Docs |
| 03 Production OEE (supplementary) | Line-level production efficiency (OEE) recaps and data. Optional context on how cold-chain capacity affects production. | 2 Docs, 2 Sheets |

## Anonymization

- The company, plant locations, controller vendor, people, and customer and retail brand names have been replaced or removed.

- Plants are labeled **Plant A**, **Plant B** and **Plant C**. People are referred to by role, for example "the Plant B operator".

- One point name contained a packaging brand and is renamed **Vacuum Packaging Area** in every file.

- Every reading, timestamp, unit, point ID (UC-5, HPR V1 Level, V-4, C-01 and so on) and sensor fault is preserved exactly as exported, including obviously bad values.

- Column spacing in the text exports was normalized to single spaces. No values were changed.

- Please do not try to re-identify the source company.

## Raw export inventory

File names follow Plant{A|B|C}_{date}_{report}.txt.

| **Date** | **Plant A (2 reports)** | **Plant B (up to 6 reports)** | **Plant C (1 report)** |
| --- | --- | --- | --- |
| 2026-06-01 | System Monitor Points; Valve Group with Setpoints | Area Temps & Vessels; Compressors 1–4; Valve Group with Setpoints | Temperature Report |
| 2026-06-02 | both | Area Temps & Vessels; Valve Group (compressor reports missing) | Temperature Report |
| 2026-06-04 | both | not exported | Temperature Report |
| 2026-06-05 | none | Area Temps & Vessels; Compressor 1 (headers say 06-05, data is for 06-04) | none |
| 2026-06-09 | both | Area Temps & Vessels; Compressors 1–4 (no Valve Group) | Temperature Report |
| 2026-06-10 | both | all 6 | none |
| 2026-06-25 | both | all 6 | Temperature Report |
| 2026-06-28 | both | all 6 | Temperature Report |
| 2026-06-30 | both | all 6 | none |

Reviews exist for June 1, 2, 4, 9, 25 and 30. There is no data for June 3 (a controller reboot) and no reviews for June 5–8.

## How to read a report

- **Header:** each file opens with a header naming the company, plant, date and report group. The header repeats at every page break.

- **Points:** each point has three lines:

- The point name.

- 24 hourly values (hours 00–23) followed by the units.

- A summary line: High = … at HH:MM  Low = … at HH:MM  Average = ….

- **Summary vs hourly values:** the summary line is computed from 15-minute samples, so it won't match the hourly values. Some summary times fall off the 15-minute grid, which suggests event-driven samples.

- **Units:**

- °F

- psig

- % Col (vessel liquid level)

- %FLA (compressor motor load)

- % (slide valve)

- PSID

- Cycles (transfer counts)

- **Setpoints:** these appear as separate "SPT …" points in the Valve Group reports.

- **Report groups:**

- Plant A: System Monitor Points (temperatures, pressures, vessel levels, ambient) and Valve Group with Setpoints.

- Plant B: Area Temperatures and Vessels, Compressor 1–4 Readings, and Valve Group with Setpoints.

- Plant C: a single Temperature Report that includes ambient air.

## Known data quirks (these are features, not bugs)

- **Dead sensors:** some Plant B points (UC-7 Boxing and Dock, and on some days UC-4 Filling Room) read 459.6 every hour, while the summary line says −459.67. That is absolute zero, which means a disconnected sensor. The hourly rows also drop the minus sign.

- **Drifting sensors:** Plant C's Back Dock Temp reads 160–283°F on early-June days, then recovers on June 4.

- **Missing setpoints:** every Plant B setpoint channel reads 0.0. "Normal" has to be learned from history.

- **Duplicate points:** some points appear twice in the same report, for example Plant A UC-3/4 Pre-Weigh and Plant B V-2 Intercooler Pres.

- **Summaries disagree between reports:** the same point can report slightly different averages in two reports from the same night.

- **Summary lows below every hourly value:** some summary lows are far below all hourly values, such as Plant A V4 Pump Op Pressure. Brief transients are only visible in the summary line.

- **Odd units:** Plant A UC-1 Engine Room is a temperature but its unit reads "Setpoin".

- **Regime changes:** spiral freezers sit warm when they are off, then pull down to −30°F or below at startup.

- **Recurring events:** Plant A UF-3/UF-4 spike at exactly 02:45 every night, growing over the month.

## Key events to find

- **06-09, Plant A:** the HPR receiver sat at 0% from 09:00 to 13:00, discharge pressure fell to 77 psig, and every cooler warmed at once.

- **06-09, Plant B:** a C-1 compressor oil leak, valved off and pumped out. Ammonia peaked at 272 ppm in the engine room. The plant switched to C-2 + B-1.

- **06-01 to 06-25, Plant A:** the 02:45 QFM freezer spike escalated, from about 24°F to 49°F against an 18°F setpoint.

- **06-30, Plant A:** the engine room averaged about 102°F against a 75°F setpoint.

## Suggested first exercises

- **Parse the exports:** write a parser for all three report formats that outputs one tidy table: plant, date, report, point, hour, value, unit.

- **Inventory and flag:** build the point inventory and flag every data-quality issue listed above automatically.

- **Check a review:** pick one review and check every number in it against the raw files. At least one review contains a number that doesn't match its source.

- **Generate synthetic data:** build a generator that extends this history into months of data, with labeled, seeded faults.