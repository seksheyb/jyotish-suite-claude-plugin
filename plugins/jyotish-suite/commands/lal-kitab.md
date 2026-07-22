---
description: Run a Lal Kitab reading — natal, rin diagnosis, varshphal, or upaay (Pt. Roop Chand Joshi's Farmans).
argument-hint: [reading type — natal | rin | family | varshphal | upaay]
---

The user has invoked `/lal-kitab`. Trigger the `lal-kitab` skill immediately.

Workflow:
1. Read `skills/lal-kitab/SKILL.md` and follow it exactly.
2. If the user has not yet given their chart or birth data, ask for either a pasted Vedic D1 chart or their birth date, exact time, and place (only the D1 is used — Lal Kitab uses no D9 and no Vimshottari).
3. Re-map the chart to Lal Kitab's fixed-house frame (Aries always 1st), compute pakka ghar status, and identify sleeping planets.
4. Ask the user (or infer from arguments) which reading mode they want: natal, rin diagnosis (Pitri / Matri / Stri / Kanya / Bhratra / Atma), family chart impact, varshphal, or upaay.
5. Deliver the reading with ranked upaay and Farman citations per the skill's methodology.

Any extra context the user passed: $ARGUMENTS
