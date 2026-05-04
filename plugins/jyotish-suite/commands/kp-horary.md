---
description: Answer a specific question via KP horary using a number 1–249 and the moment + place of asking.
argument-hint: [horary number 1-249] [your question]
---

The user has invoked `/kp-horary`. Trigger the `kp-horary` skill immediately.

Workflow:
1. Read `skills/kp-horary/SKILL.md` and follow it exactly.
2. Collect the three required inputs if not yet provided:
   - A horary number between 1 and 249
   - The exact moment of the question (date, time, timezone)
   - The location of the questioner (city / lat-lon)
   - The specific question being asked
3. Compute the horary chart from scratch using `pyswisseph` (KP New ayanamsa, Placidus cusps) — use the scripts under `skills/kp-horary/scripts/`.
4. Compute Ruling Planets with full calculation shown.
5. Run cuspal sub-lord analysis with the question-specific house combinations defined in the skill.
6. Cross-check via Ruling Planets.
7. Deliver verdict + timing window + confidence level.

If a script under `skills/kp-horary/scripts/` fails with `ModuleNotFoundError: No module named 'swisseph'`, instruct the user to run `pip install pyswisseph` in their Python environment and retry.

Any extra context the user passed: $ARGUMENTS
