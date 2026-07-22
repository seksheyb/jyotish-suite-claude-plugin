---
description: Answer a specific question via KP horary using a number 1–249 and the moment + place of asking.
argument-hint: [horary number 1-249] [your question]
---

The user has invoked `/kp-horary`. Trigger the `kp-horary` skill immediately.

Workflow:
1. Read `skills/kp-horary/SKILL.md` and follow it exactly — it is a wave orchestrator.
2. Collect the required inputs if not yet provided:
   - A horary number between 1 and 249
   - The exact moment of the question (date, time, timezone)
   - The location of the questioner (city / lat-lon)
   - The specific question being asked
3. The horary chart, Ruling Planets, cusps, and significators are computed deterministically by the shared baseline script (`scripts/compute_kp_horary_baseline.py`, KP New ayanamsa, Placidus cusps) — never hand-derive them.
4. Deliver verdict + timing window + confidence level per the skill's wave flow (cuspal sub-lord analysis, RP cross-check, dasha alignment, transit confirmation).

If a script under the shared `plugins/jyotish-suite/scripts/` or `lib/` directory fails with `ModuleNotFoundError: No module named 'swisseph'`, instruct the user to run `pip install pyswisseph` in their Python environment and retry.

Any extra context the user passed: $ARGUMENTS
