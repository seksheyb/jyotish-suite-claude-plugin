---
description: Run a deep Vedic (Parashari) chart reading from a pasted chart or birth data.
argument-hint: [optional notes — focus area, life domain, time horizon]
---

The user has invoked `/vedic-astro`. Trigger the `vedic-astro` skill immediately.

Workflow:
1. Read `skills/vedic-astro/SKILL.md` and follow it exactly — it is a wave orchestrator.
2. If the user has not yet given their chart or birth data, ask for either a pasted D1 chart (with degrees — the D9 Navamsa is derived automatically) or their birth date, exact time, and place, per the chart-intake format in the skill.
3. Show the rendered chart back for verification and wait for explicit confirmation before any analysis.
4. Deliver a multi-layered Vedic reading covering Nakshatras, Padas, degrees, aspects, Vimshottari Dasha, and composite synthesis — per the skill's methodology.

Any extra context the user passed: $ARGUMENTS
