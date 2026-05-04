---
description: Run a KP (Krishnamurti Paddhati) natal reading or event-timing prediction.
argument-hint: [life-reading | event timing — area + horizon]
---

The user has invoked `/kp-natal`. Trigger the `kp-natal` skill immediately.

Workflow:
1. Read `skills/kp-natal/SKILL.md` and follow it exactly.
2. If the user has not yet provided a pre-computed natal KP chart (markdown with cuspal positions, planetary positions with full lord chain, significators, dasha sequence), ask for it.
3. Echo back the parsed chart for verification.
4. Ask conversationally whether the user wants a life reading or event timing — if event timing, get the area (career, marriage, finance, etc.) and the horizon.
5. Compute current Ruling Planets with full calculation shown.
6. Compute Sookshma dasha (4th level) for the relevant window.
7. Deliver a structured KP reading with cuspal sub-lord analysis, significators, and timing window.

If a script under `skills/kp-natal/scripts/` fails with `ModuleNotFoundError: No module named 'swisseph'`, instruct the user to run `pip install pyswisseph` in their Python environment and retry.

Any extra context the user passed: $ARGUMENTS
