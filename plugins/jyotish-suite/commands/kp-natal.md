---
description: Run a KP (Krishnamurti Paddhati) natal reading or event-timing prediction.
argument-hint: [life-reading | event timing — area + horizon]
---

The user has invoked `/kp-natal`. Trigger the `kp-natal` skill immediately.

Workflow:
1. Read `skills/kp-natal/SKILL.md` and follow it exactly — it is a wave orchestrator.
2. If the user has not yet given their chart or birth data, ask for either a pasted natal KP chart (cuspal positions with lord chains, planetary positions, significators, dasha sequence) or their birth date, exact time, and place — the chart is computed via the shared ephemeris layer.
3. Show the rendered chart back for verification and wait for explicit confirmation before any analysis.
4. Ask conversationally whether the user wants a life reading or event timing — if event timing, get the area (career, marriage, finance, etc.) and the horizon.
5. Deliver the structured KP reading per the skill's wave flow (baseline sidecar, cuspal sub-lord analysis, Ruling Planets, dasha windows, transit confirmation).

If a script under the shared `plugins/jyotish-suite/scripts/` or `lib/` directory fails with `ModuleNotFoundError: No module named 'swisseph'`, instruct the user to run `pip install pyswisseph` in their Python environment and retry.

Any extra context the user passed: $ARGUMENTS
