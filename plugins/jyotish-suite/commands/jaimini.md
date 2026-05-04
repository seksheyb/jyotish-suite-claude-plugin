---
description: Run a Jaimini reading — Chara Karakas, Arudha Padas, Swamsha, Argala, Chara Dasha.
argument-hint: [optional notes — life domain or timing question]
---

The user has invoked `/jaimini`. Trigger the `jaimini-astrology` skill immediately.

Workflow:
1. Read `skills/jaimini-astrology/SKILL.md` and follow it exactly.
2. If the user has not yet provided a pre-computed D1 + D9 chart, ask for it.
3. Echo the parsed chart back for verification.
4. Compute the Jaimini baseline: Chara Karakas, Arudha Padas, Swamsha, Argala, Chara Dasha.
5. Deliver the Jaimini reading using the rigorous methodology defined in the skill.

Any extra context the user passed: $ARGUMENTS
