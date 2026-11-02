# plant_c

Not started. Plan for the Plant C baseline.

## What makes Plant C different

- One temperature report, no setpoints, no pressures, no compressor data.
- Normal must be learned from history only.
- Back Dock Temp is a failing sensor (130-283 F) in two periods; hourly values above 130 F are already blank.
- Six real June days (June 1, 2, 4, 9, 25 and 28). There is no Plant C data for June 10 or June 30.
- Six missing days in the other months.

## Events to find

E21 and E22 (Back Dock drift, suppress as sensor fault), E23 (Queso Cup Chiller about 10 F warm until 07-22), E24 (Protein Room Front chronically warm until 08-05), E25 (Freezer slowly warming in Aug-Sep).

## Plan

- [ ] Hour-of-day normals per room, trained on Apr-May
- [ ] Persistence rule (above 41 F for cold rooms) and plant-wide grouping
- [ ] Step-change detection (change point) for E23
- [ ] Slow trend (Theil-Sen) for E25
- [ ] Learn what chronic means for Protein Room Front so it becomes one standing alert, not a daily one
- [ ] Score with `../evaluation/`

## Watch out

Blast Freezer is production-cycled (wide swings are normal). Compare each room with its own history only.
