# Cold Chain Monitor: Front-End Requirements

Audience: designers and front-end developers.
Product: a web app that tracks refrigeration systems at three plants, ranks problems by priority, and notifies people when something is High or Critical.
Nature of the product: a tracking and notifying tool. It advises people and never controls equipment.

Status of numbers: thresholds, times and limits below are defaults to confirm with the client. They are marked (TBC).

---

## 1. Users and what they need to do

| Role | Who they are | Main tasks | Device |
|---|---|---|---|
| Viewer | Plant lead, quality, executives | See status, read alerts, read the daily digest | Desktop, some phone |
| Operator | Refrigeration tech, on-call | Acknowledge alerts, add notes, mark resolved | Phone first |
| Plant manager | Manager of one plant | Everything an Operator does, change priority, add maintenance windows | Desktop and phone |
| Admin | Client IT or the project team | Users, on-call roster, notification routes, thresholds, setpoints | Desktop |

Users only see the plants assigned to them. Admins see all three.

The most important design target is a tired on-call tech on a phone at 3 a.m. who needs to understand one alert and acknowledge it in under 30 seconds.

---

## 2. Priority system

Five states. Every status shown anywhere in the app uses these.

| Priority | Meaning | Typical example | Push notification? | Response target (TBC) |
|---|---|---|---|---|
| Healthy | Inside learned normal range | n/a | No | None |
| Low | Slow drift or recurring pattern | Freezers spike every night at 02:45 and the spike is growing | No (daily digest) | Next day |
| Medium | One room out of its normal band, or a sensor fault needing maintenance | Dead temperature sensor in a filling room | No (daily digest) | Same shift or next business day |
| High | Food-safety room above 41°F for 30+ minutes, or several rooms warming at once | Four coolers at 52–55°F at the same time | Yes: SMS, Slack or Teams, email | Acknowledge within 1 hour |
| Critical | Ammonia alarm, receiver at 0% during production, compressor trip with no backup | Receiver level 0% for hours during production | Yes: SMS and phone call, repeated until acknowledged | Now |

Also shown, but not a priority:
- Suppressed: a deviation with a known cause (planned maintenance, a known dead sensor, a planned shutdown). It never notifies anyone. It is visible in the app with the reason.
- Data issue: missing or invalid data (see Data health).

Design rules for priority:
- Never rely on colour alone. Every priority has a colour, an icon and a text label.
- Suggested hue family: Healthy green, Low blue, Medium amber, High orange, Critical red. Check that Low/Medium and High/Critical are distinguishable for colour-blind users.
- Critical must look clearly more urgent than High, for example a solid fill against an outlined High badge.
- The same badge component is used on tiles, rows, charts, notifications and emails.

Alert states: Open, Notified, Acknowledged, Resolved. Suppressed items are shown in their own list.

---

## 3. Navigation

Desktop: left sidebar. Phone: bottom tab bar with the first four items.

1. Overview
2. Alerts
3. Plants
4. Data health
5. Settings (Admin and Plant manager only)

A global header shows: the selected plant filter, last-data-received time, the signed-in user, and a notifications indicator.

---

## 4. Screens

For each screen: purpose, content, interactions, states.

### S1. Overview (home)
Purpose: answer "is anything wrong right now, and where?" in 5 seconds.

Content:
- A summary strip: counts of open Critical, High, Medium, Low alerts across the user's plants.
- One tile per plant (A, B, C): plant name, worst current priority badge, open alert count, a one-line headline of the worst alert, and "Last data: 6:42 a.m." with a stale-data warning if overdue.
- An "Needs acknowledgement" list: High and Critical alerts not yet acknowledged, with the escalation countdown.
- A "Recent activity" feed: new, acknowledged and resolved alerts.

Interactions: tile opens the Plant page; alert row opens Alert detail; plant filter in the header.

States: empty ("No open alerts. All plants healthy."), loading skeletons, a banner when data is late or the notifier is failing.

### S2. Plants and plant page
Purpose: see every room and system in one plant.

Content:
- Grouped list or grid by area: rooms and coolers, freezers, engine room, receiver and vessels, compressors.
- Each row: name, status badge, current value with unit, deviation from setpoint or normal, a small 24-hour sparkline, and a flag chip if the data is invalid (for example "Sensor offline").
- Filters: priority, area, show flagged only.

Interactions: row opens Point detail; sort by priority or name.

States: points with no setpoint show "No setpoint, using learned normal range". Points with invalid data show the flag chip and a hatched sparkline.

### S3. Point detail
Purpose: investigate one reading.

Content:
- A time-series chart with ranges 24 hours, 7 days, 30 days and custom.
- On the chart: the learned normal band (shaded), the setpoint line (dashed, when one exists), and alert markers.
- Overlay toggles: work orders, shift-log entries, dock door events, production and sanitation windows, outdoor temperature, "compare with yesterday".
- Invalid data (dead sensor, outage, stuck value) is drawn as a gap with a hatched background, never as a line, with a tooltip explaining why.
- Tooltip shows time, value, deviation and quality flag.
- A side panel: current value, setpoint, normal range for this hour, open alerts on this point, recent work orders.

States: empty history, partial data, chart error.

### S4. Alert inbox
Purpose: triage all alerts.

Content:
- Default sort: priority first, then newest.
- Row: priority badge, title, plant and location, status, started time, duration, owner, and (for High/Critical not yet acknowledged) an escalation countdown.
- Filters: priority, plant, status, time range, "assigned to me".
- Tabs: Active, Resolved, Suppressed.

Interactions: row opens Alert detail; acknowledge directly from the row (Operator and above); bulk acknowledge is allowed for Low and Medium only.

States: empty per tab, loading, error.

### S5. Alert detail (most important screen)
Purpose: understand one alert and act.

Content, top to bottom:
1. Header: priority badge, title in plain language, plant and location, status, started time, duration so far.
2. Action bar: Acknowledge, Add note, Mark resolved, Change priority (Plant manager and above). Critical acknowledgement asks for a confirmation and an optional note.
3. "What happened": 1–3 sentences, no jargon. Example: "Four coolers rose from about 36°F to 53°F at the same time and stayed above 41°F for about 3 hours."
4. "Likely cause": a plain-language suggestion with a confidence indicator (for example "Likely: receiver level at 0%").
5. "What to check": 2–4 short suggested checks.
6. Evidence: a chart of the affected readings with the alert window highlighted, and a table of the key readings (point, value, time).
7. Related records: matching work orders, shift-log entries, dock events, weather, with links.
8. "Who has been told": a notification log (person, channel, sent, delivered, acknowledged) and the escalation timer.
9. Timeline: created, notified, acknowledged, notes, priority changes, resolved, each with who and when.

States: suppressed alert shows a banner at the top with the reason ("Known sensor fault, work order WO-26504"). A resolved alert is read-only.

### S6. Mobile acknowledge page (opened from an SMS or Slack link)
Purpose: acknowledge fast.

Content: a full-width priority banner, one-line summary, location, started time, a large Acknowledge button, a secondary "Open full details" link. After acknowledging, show who else has been told and what happens next.

Design assumption: the user must sign in, but the sign-in should be quick (single sign-on if available). Confirm with the client.

### S7. Data health
Purpose: show what the system cannot see, so silence is never mistaken for health.

Content:
- Data feed status per plant: last file received, expected next, reports expected vs received for today.
- A calendar view of missing reports and report groups.
- A list of sensor problems: dead sensor, stuck value (flat line), drifting or implausible readings, with the first and last day affected and the linked work order.
- Outages: for example "No data after 2:00 p.m. on Sep 15 (controller communication lost)".
- Notifier health: last test message, failed sends.

Interactions: row opens the affected point; "Create work order note" is out of scope for phase 1.

### S8. Maintenance windows and suppression (Plant manager and Admin)
Purpose: stop planned work from paging anyone.

Content: a list and a calendar of windows (plant, equipment or room, start, end, reason, created by, status). A form to add or edit a window; the form shows what will be suppressed. A list of known sensor faults being ignored, each with an end date or "until fixed".

States: a window that is active shows a banner on the affected Point and Plant pages.

### S9. Notification settings (Admin)
Content: per-plant on-call roster (name, phone, Slack or Teams handle, email, days and hours), routing table by priority (who gets what, by which channel), escalation steps and times (TBC), quiet-hours rules for Low and Medium digests, "send test notification" button.

### S10. Thresholds and setpoints (Admin and Plant manager)
Content: a table of points with editable setpoint, high and low limits, and priority mapping. Plants B and C may not have usable setpoints, so setpoints are optional and the table shows "learned normal" in that case. Edits are logged. A "restore default" action per row.

### S11. Users and audit log (Admin)
Content: user list with role and plant assignment; an audit log of acknowledgements, priority changes, setting changes and notification outcomes (who, what, when, before and after values); CSV export.

### S12. Sign in
Single sign-on button when configured, otherwise email and password with a reset flow. Session timeout message that returns the user to where they were.

---

## 5. Notification content (also needs design)

Short message (SMS, Slack or Teams):
`CRITICAL · Plant A · Receiver level 0% since 9:00 a.m. during production. Rooms warming. Acknowledge: <link>`

Rules: priority first, plant second, one plain sentence, one link. Under 160 characters for SMS where possible.

Daily digest email (to plant leads): subject "Plant A daily summary: 2 Low, 1 Medium, data issue". Body: a status line per plant, open Low and Medium alerts, data-health issues, alerts resolved yesterday, a link to the app.

Escalation message: "Not acknowledged for 15 minutes (TBC): Critical at Plant A has now been sent to the plant manager."

---

## 6. Key user flows to design

1. Critical alert at night: SMS arrives, user taps the link, sees the mobile acknowledge page, taps Acknowledge, sees confirmation, then opens details.
2. Escalation: an alert is not acknowledged in time, the countdown reaches zero, the next person is notified, and the original owner sees "escalated".
3. Investigate a High alert: Overview, then the alert row, then Alert detail, then the chart for one affected room, then the work orders overlay.
4. Plan maintenance: Maintenance windows, add a window for a compressor, confirm what will be suppressed, save, and see the banner on that equipment.
5. Understand a quiet plant: a plant shows no alerts but its feed is late, and the Overview shows a stale-data warning instead of a green tile.
6. Change an on-call person: Settings, edit the roster, send a test message.

---

## 7. Components to design

Priority badge and status badge; plant tile; alert row and alert card; escalation countdown chip; time-series chart with band, setpoint, markers and hatched gaps; sparkline; flag chip (Sensor offline, Data missing, Stuck value, Out of range); notification log table; timeline; banners (stale data, active maintenance window, notifier failure); confirmation dialog; toast; filter bar; calendar; form fields for windows and thresholds; empty and error states.

---

## 8. Sample content for mock-ups

Use these so mock-ups show realistic text.

| Priority | Plant | Title | Detail |
|---|---|---|---|
| Critical | Plant A | Receiver level at 0% during production | 9:00 a.m. to 1:00 p.m.; discharge pressure fell from 154 to 77 psig; every cooler warmed 4–8°F |
| High | Plant A | Four coolers above 41°F at the same time | UC-5, UC-6, UC-7, UC-8 at 52–55°F around 10:30 a.m. |
| High | Plant B | Compressor C-1 shut down after an oil leak | C-1 load dropped to 0%; backup compressors restarted at 9:17 p.m. |
| Medium | Plant B | Filling room temperature sensor not reading | Reports −459.67°F (disconnected); work order open |
| Low | Plant A | Freezers UF-3 and UF-4 spike every night at 2:45 a.m. | Peaks grew from about 24°F to 49°F against an 18°F setpoint |
| Low | Plant C | Freezer slowly warming over about 9 weeks | Weekly average rose from about −4°F to about 0°F |
| Suppressed | Plant B | Compressor power interruption, Aug 19 | Known cause: utility power blip; compressors restarted by 3:20 p.m. |
| Data issue | Plant A | Controller data missing after 2:00 p.m., Sep 15 | Export wrote zeros; controller lost communication |

Example "What happened" text (Alert detail):
"Freezers UF-3 and UF-4 both rose to about 49°F at 2:45 a.m. last night, against an 18°F setpoint. The same spike has happened at the same time every night this week and it is getting larger."

---

## 9. Responsive and device rules

Phone-first screens: Alert detail, Mobile acknowledge page, Alert inbox, Overview.
Desktop-first screens: Point detail (charts), Data health, all Settings screens.

On phone: charts default to 24 hours, filters collapse into a single sheet, tables become cards. Tap targets at least 44 px. Acknowledge is reachable with one thumb.

---

## 10. UX and accessibility rules

- Time: always show plant-local time with the plant name when more than one plant is shown. Use relative time ("42 min ago") with absolute time on hover or tap.
- Units: always show units (°F, psig, %). Show deviations with a sign (+3.2°F).
- Language: plain sentences. Avoid controller jargon in headlines; show the technical point name in a secondary line.
- Colour contrast meets WCAG AA. Status is never conveyed by colour alone.
- Keyboard accessible, visible focus, screen-reader labels on badges and chart summaries (a text summary under every chart).
- Destructive or hard-to-reverse actions (change priority, silence, mark resolved on Critical) need a confirmation and are logged.
- Auto-refresh every 60 seconds (TBC) with a visible "Updated 12 s ago"; never move content under the user's cursor.
- No sound or flashing on the page.

---

## 11. Performance expectations that affect design

- Overview and Alert inbox appear in under 3 seconds with a year of data.
- Charts load the visible range only and aggregate long ranges (for example hourly for 30 days).
- A new alert appears in the app within 1 minute of being created.

---

## 12. Out of scope for the first design

- Any control of equipment or setpoints.
- Field or offline mobile app.
- Forecast views and the written daily review (design later).
- Creating or editing work orders inside the app.

---

## 13. Open design questions for the client

1. Does the client have faster-than-nightly data, and what feed? This decides whether "Critical, now" is realistic.
2. Do they use single sign-on? This affects the sign-in and mobile acknowledge pages.
3. Which messaging channels does each plant use: SMS, Slack, Teams?
4. Are the 41°F, 30-minute and escalation timings final?
5. Do they have a brand style guide and logo?
6. Which languages are needed?

---

## 14. Suggested design deliverables

1. Priority and status badge system, with a short colour and accessibility note.
2. Wireframes for S1, S2, S3, S4, S5, S6, S7.
3. Mobile versions of S1, S4, S5, S6.
4. The three notification templates (short message, daily digest, escalation).
5. Clickable prototype of flow 1 (Critical alert at night) and flow 4 (plan maintenance).
