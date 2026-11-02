# 03_frontend_design

Design of the monitoring and notifying web app the client will use to watch the refrigeration systems and be told when something is High or Critical.

It is a tracking and notifying tool. It advises people and never controls equipment.

| Folder | What goes there |
|---|---|
| [`requirements/`](requirements/README.md) | The front-end requirements (screens, flows, components, content) |
| [`wireframes/`](wireframes/README.md) | Low-fidelity screens |
| [`design_system/`](design_system/README.md) | Priority badges, colours, type, components |
| [`prototypes/`](prototypes/README.md) | Clickable prototypes of the key flows |
| [`sample_content/`](sample_content/README.md) | Realistic alert content for mock-ups |

Also read `docs/webapp_requirements_and_system_design.md` for the system design, the priority table and the functional requirements.

## Design target

A tired on-call tech on a phone at 3 a.m. must understand one alert and acknowledge it in under 30 seconds.

## Priority system (used everywhere)

Healthy, Low, Medium, High, Critical, plus Suppressed and Data issue. Only High and Critical send push notifications. Never rely on colour alone: every priority has a colour, an icon and a text label.

## Screens and status

| # | Screen | Platform first | Priority | Status |
|---|---|---|---|---|
| S1 | Overview | Phone and desktop | First release | Not started |
| S2 | Plants and plant page | Desktop | First release | Not started |
| S3 | Point detail (chart) | Desktop | First release | Not started |
| S4 | Alert inbox | Phone | First release | Not started |
| S5 | Alert detail | Phone | First release | Not started |
| S6 | Mobile acknowledge page | Phone | First release | Not started |
| S7 | Data health | Desktop | First release | Not started |
| S8 | Maintenance windows | Desktop | Second release | Not started |
| S9 | Notification settings | Desktop | Second release | Not started |
| S10 | Thresholds and setpoints | Desktop | Second release | Not started |
| S11 | Users and audit log | Desktop | Second release | Not started |
| S12 | Sign in | Both | First release | Not started |

## Deliverables checklist

- [ ] Priority and status badge system with a short colour and accessibility note
- [ ] Wireframes for S1, S2, S3, S4, S5, S6, S7
- [ ] Mobile versions of S1, S4, S5, S6
- [ ] The three notification templates (short message, daily digest, escalation)
- [ ] Clickable prototype of the Critical alert at night and of planning a maintenance window

## Handoff rules

- Export frames as PNG into `wireframes/` and keep the source file link in that folder's README.
- Name frames `S5_alert_detail_mobile_v1`. Bump the version instead of overwriting.
- Use the sample alerts in `sample_content/` so mock-ups show realistic text.
- Record each design decision that changes a requirement in `requirements/` with a date.

## Open questions for the client

Faster-than-nightly data feed, single sign-on, messaging channels per plant (SMS, Slack, Teams), final thresholds and escalation times, brand style guide, languages.
